from flask import (
    Flask, request, session, redirect, url_for,
    render_template_string, g
)

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
def attach_current_user():
    """Her istekte oturumdaki kullanıcıyı g.current_user içine koy."""
    g.current_user = get_current_user()


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
        csrf = generate_csrf_token()
        return render_template_string(
            LOGIN_TEMPLATE,
            csrf=csrf,
            error="Wrong credentials."
        )

    login_user(email)
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
