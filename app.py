import json
import os


from security.bruteforce_protection import (
    is_blocked,
    register_failed_attempt,
    reset_attempts,
    get_retry_after,
)


from flask import (
    Flask, request, session, redirect, url_for,
    render_template_string, g
)

from security.validation_firewall import run_validation_firewall

from honeypot.routes import honeypot_bp
from middleware import BehaviorEngineMiddleware

from security.validation import (
    validate_email,
    validate_password,
    sanitize_text,
)
from security.auth import (
    login_user,
    logout_user,
    login_required,
    role_required,
    get_current_user,
    USERS,
)
from security.csrf import generate_csrf_token, validate_csrf
from security.logging_secure import secure_log


app = Flask(__name__)
app.secret_key = "dev-secret-key"  # TODO: production ortamında env üzerinden alınmalı

# Behaviour engine middleware entegrasyonu
app.wsgi_app = BehaviorEngineMiddleware(app)

# Honeypot blueprint entegrasyonu
app.register_blueprint(honeypot_bp)

@app.before_request
def validation_firewall_hook():
    # (opsiyonel) whitelist: honeypot/static vs skip
    # if request.path.startswith("/admin-panel") or request.path.startswith("/static"):
    #     return None

    if not run_validation_firewall(request):
        secure_log(
            "request_blocked_by_validation_firewall",
            {"reason": "payload_detected"},
            level="WARN",
            ip=request.remote_addr,
            path=request.path,
            user=session.get("user_email"),
            session_id=session.get("session_id"),
        )
        return "Request blocked by Validation Firewall.", 400

    

  


@app.before_request
def attach_current_user():
    """Her istekte oturumdaki kullanıcıyı g.current_user içine koy."""
    g.current_user = get_current_user()

@app.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-XSS-Protection", "1; mode=block")
    return response

# ==========================
# Authentication & Session
# ==========================

LOGIN_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Login – Neon Immune Web Grid</title>
</head>
<body>
<h1>Login</h1>
<form method="post">
    <input type="hidden" name="csrf_token" value="{{ csrf }}">
    <label>Email:
        <input name="email" type="text" autocomplete="username" required>
    </label><br>
    <label>Password:
        <input name="password" type="password" autocomplete="current-password" required>
    </label><br>
    <button type="submit">Login</button>
</form>
{% if error %}
<p style="color:red">{{ error }}</p>
{% endif %}
<p><a href="{{ url_for('index') }}">Back to home</a></p>
</body>
</html>
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        csrf = generate_csrf_token()
        return render_template_string(LOGIN_TEMPLATE, csrf=csrf, error="")

    csrf = request.form.get("csrf_token")
    if not validate_csrf(csrf):
        secure_log("csrf_failed", {
            "ip": request.remote_addr,
            "path": request.path,
        })
        return "CSRF token invalid", 400

    email = (request.form.get("email") or "").strip()
    password = request.form.get("password") or ""

    identifier = f"{request.remote_addr}:{email or 'unknown'}"

    if is_blocked(identifier):
        retry_after = get_retry_after(identifier) or 0
        secure_log("login_bruteforce_blocked", {
            "email": email,
            "ip": request.remote_addr,
            "retry_after": retry_after,
        })
        return (
            f"Too many failed attempts. Try again in {retry_after} seconds.",
            429,
            {"Retry-After": str(retry_after)},
        )

    if not validate_email(email) or not validate_password(password):
        secure_log("login_failed_validation", {
            "email": email,
            "ip": request.remote_addr,
        })
        csrf = generate_csrf_token()
        return render_template_string(
            LOGIN_TEMPLATE,
            csrf=csrf,
            error="Invalid email or password format."
        )

    user = USERS.get(email)
    if not user or user["password"] != password:
        secure_log("login_failed_credentials", {
            "email": email,
            "ip": request.remote_addr,
        })
        register_failed_attempt(identifier)
        csrf = generate_csrf_token()
        return render_template_string(
            LOGIN_TEMPLATE,
            csrf=csrf,
            error="Wrong credentials."
        )

    login_user(email)
    reset_attempts(identifier)
    secure_log("login_success", {
        "email": email,
        "ip": request.remote_addr,
        "role": user["role"],
    })

    return redirect(url_for("user_dashboard"))


@app.route("/logout")
@login_required
def logout():
    email = session.get("user_email")
    logout_user()
    secure_log("logout", {
        "email": email,
        "ip": request.remote_addr,
    })
    return redirect(url_for("login"))


# ==========================
# Dashboards & Access Control
# ==========================

USER_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>User Dashboard – Neon Immune Web Grid</title>
</head>
<body>
<h1>User Dashboard</h1>
<p>Welcome {{ email }} (role: {{ role }})</p>
<ul>
    <li><a href="{{ url_for('admin_dashboard') }}">Admin / Security Panel</a></li>
    <li><a href="{{ url_for('index') }}">Home</a></li>
    <li><a href="{{ url_for('logout') }}">Logout</a></li>
</ul>
</body>
</html>
"""


@app.route("/dashboard/user")
@login_required
def user_dashboard():
    user = g.current_user
    return render_template_string(
        USER_TEMPLATE,
        email=sanitize_text(user["email"]),
        role=user["role"],
    )


ADMIN_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Admin / Security Panel – Neon Immune Web Grid</title>
</head>
<body>
<h1>Admin / Security Panel</h1>
<p>Welcome {{ email }} (role: {{ role }})</p>
<p>This area is protected by role-based access control.</p>
<ul>
    <li><a href="{{ url_for('user_dashboard') }}">User Dashboard</a></li>
    <li><a href="{{ url_for('index') }}">Home</a></li>
    <li><a href="{{ url_for('logout') }}">Logout</a></li>
</ul>
</body>
</html>
"""


@app.route("/dashboard/admin")
@login_required
@role_required("admin", "security")
def admin_dashboard():
    user = g.current_user
    return render_template_string(
        ADMIN_TEMPLATE,
        email=sanitize_text(user["email"]),
        role=user["role"],
    )
# ==========================
# Security Policy Management (Week 4)
# ==========================



POLICY_FILE = os.path.join("security", "policy_store.json")

def _read_policy():
    with open(POLICY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _write_policy(p):
    with open(POLICY_FILE, "w", encoding="utf-8") as f:
        json.dump(p, f, indent=2, ensure_ascii=False)


@app.route("/security/policy", methods=["GET"])
@login_required
@role_required("admin", "security")
def view_policy():
    return _read_policy(), 200


@app.route("/security/policy/blacklist-ip", methods=["POST"])
@login_required
@role_required("admin", "security")
def add_blacklist_ip():
    ip = (request.form.get("ip") or "").strip()
    if not ip:
        return {"error": "ip required"}, 400
    p = _read_policy()
    if ip not in p["blacklist_ips"]:
        p["blacklist_ips"].append(ip)
    _write_policy(p)
    secure_log("policy_blacklist_ip_added", {"ip": ip}, level="WARN", user=session.get("user_email"), ip=request.remote_addr, path=request.path)
    return {"ok": True, "blacklist_ips": p["blacklist_ips"]}, 200


@app.route("/security/policy/whitelist-path", methods=["POST"])
@login_required
@role_required("admin", "security")
def add_whitelist_path():
    path = (request.form.get("path") or "").strip()
    if not path.startswith("/"):
        return {"error": "path must start with /"}, 400
    p = _read_policy()
    if path not in p["whitelist_paths"]:
        p["whitelist_paths"].append(path)
    _write_policy(p)
    secure_log("policy_whitelist_path_added", {"path": path}, level="INFO", user=session.get("user_email"), ip=request.remote_addr, path=request.path)
    return {"ok": True, "whitelist_paths": p["whitelist_paths"]}, 200



# ==========================
# Root
# ==========================

@app.route("/")
def index():
    return """
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Neon Immune Web Grid</title>
    </head>
    <body>
        <h1>Neon Immune Web Grid</h1>
        <p>Core application is running. Neon Immune System is active.</p>
        <ul>
            <li><a href="/login">Login</a></li>
            <li><a href="/dashboard/user">User Dashboard (requires login)</a></li>
            <li><a href="/dashboard/admin">Admin / Security Panel (admin or security role)</a></li>
            <li><a href="/admin-panel">Honeypot Test: /admin-panel</a></li>
        </ul>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True, port=5000)
