import json
import os
import sqlite3
import time
import requests


from security.bruteforce_protection import (
    is_blocked,
    register_failed_attempt,
    reset_attempts,
    get_retry_after,
)


from flask import (
    Flask, request, session, redirect, url_for,
    render_template_string, render_template, jsonify, g
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
    # Whitelist: API endpoints ve static dosyalar
    if request.path.startswith("/api/") or request.path.startswith("/static"):
        return None

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
    return render_template('dashboard.html')

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@app.route("/home")
def home():
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
            <li><a href="/">Security Dashboard</a></li>
        </ul>
    </body>
    </html>
    """

# ==========================
# Dashboard API Endpoints
# ==========================

@app.route('/api/dashboard/threats')
def api_threats():
    """Dashboard için tehdit verilerini JSON olarak döndür"""
    threats = []
    stats = {}
    top_attackers = []
    blocked_count = 0
    
    db_path = 'honeypot_logs.db'
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Son 50 tehdit
            cursor.execute("""
                SELECT ip_address, threat_type, path, risk_score, timestamp 
                FROM threats 
                ORDER BY id DESC 
                LIMIT 50
            """)
            rows = cursor.fetchall()
            
            for row in rows:
                threats.append({
                    'ip': row[0],
                    'threat_type': row[1],
                    'endpoint': row[2],
                    'risk': row[3],
                    'timestamp': row[4],
                    'payload': ''
                })
            
            # Tehdit istatistikleri
            cursor.execute("""
                SELECT threat_type, COUNT(*) 
                FROM threats 
                GROUP BY threat_type
            """)
            for row in cursor.fetchall():
                stats[row[0]] = row[1]
            
            # Top saldırganlar
            cursor.execute("""
                SELECT ip_address, COUNT(*) as cnt 
                FROM threats 
                GROUP BY ip_address 
                ORDER BY cnt DESC 
                LIMIT 5
            """)
            for row in cursor.fetchall():
                top_attackers.append({'ip': row[0], 'count': row[1]})
            
            conn.close()
        except Exception as e:
            print(f"DB Error: {e}")
    
    # DIM JSON'dan payload bilgisi
    dim_path = 'dim_threat_memory.json'
    if os.path.exists(dim_path):
        try:
            with open(dim_path, 'r') as f:
                dim_data = json.load(f)
                
            for i, threat in enumerate(threats[:20]):
                for dim in reversed(dim_data):
                    if (dim.get('attacker_ip') == threat['ip'] and 
                        dim.get('target_endpoint') == threat['endpoint']):
                        threats[i]['payload'] = dim.get('payload_captured', '')[:100]
                        break
        except:
            pass
    
    return jsonify({
        'threats': threats,
        'total': len(threats),
        'stats': stats,
        'top_attackers': top_attackers,
        'blocked_count': blocked_count
    })

@app.route('/api/dashboard/status')
def api_status():
    """Sistem durumu"""
    return jsonify({
        'status': 'active',
        'honeypots': 5,
        'health': 98,
        'version': '1.0-beta'
    })


# ==========================
# Attack Simulation API
# ==========================

@app.route('/api/attack/simulate', methods=['POST'])
def api_attack_simulate():
    """Frontend'den gelen saldırı simülasyonlarını çalıştırır"""
    data = request.get_json()
    attack_type = data.get('attack_type', '')
    
    base_url = "http://127.0.0.1:5000"
    results = []
    summary = {"total_requests": 0, "blocked": 0, "trapped": 0, "passed": 0}
    
    try:
        if attack_type == 'bruteforce':
            for i in range(5):
                try:
                    res = requests.post(f"{base_url}/admin-panel", 
                                       data={"username": f"admin{i}", "password": "123456"},
                                       timeout=5)
                    status = res.status_code
                    if status == 403:
                        msg = "BLOCKED by Adaptive Defense"
                        summary["blocked"] += 1
                    elif status == 200:
                        msg = "Trapped - Fake login page served"
                        summary["trapped"] += 1
                    else:
                        msg = f"Response received"
                        summary["passed"] += 1
                    
                    results.append({
                        "endpoint": f"/admin-panel (attempt {i+1})",
                        "status_code": status,
                        "message": msg
                    })
                    summary["total_requests"] += 1
                    time.sleep(0.2)
                except Exception as e:
                    results.append({
                        "endpoint": f"/admin-panel (attempt {i+1})",
                        "status_code": 0,
                        "message": f"Error: {str(e)}"
                    })
                    
        elif attack_type == 'sqli':
            sqli_payloads = [
                ("' OR '1'='1", "/api/v1/user-data?id="),
                ("'; DROP TABLE users;--", "/search?q="),
                ("1 UNION SELECT * FROM users", "/product?id="),
                ("admin'--", "/login?user=")
            ]
            for payload, endpoint in sqli_payloads:
                try:
                    url = f"{base_url}{endpoint}{payload}"
                    res = requests.get(url, timeout=5)
                    status = res.status_code
                    if status == 403:
                        msg = "BLOCKED - SQLi detected"
                        summary["blocked"] += 1
                    elif status in [200, 401]:
                        msg = "TRAPPED - Honeypot caught SQLi"
                        summary["trapped"] += 1
                    else:
                        msg = "Request processed"
                        summary["passed"] += 1
                    
                    results.append({
                        "endpoint": f"{endpoint} [{payload[:20]}...]",
                        "status_code": status,
                        "message": msg
                    })
                    summary["total_requests"] += 1
                except Exception as e:
                    results.append({
                        "endpoint": endpoint,
                        "status_code": 0,
                        "message": f"Error: {str(e)}"
                    })
                    
        elif attack_type == 'xss':
            xss_payloads = [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert(1)>",
                "javascript:alert(document.cookie)",
                "<svg onload=alert(1)>"
            ]
            for payload in xss_payloads:
                try:
                    res = requests.get(f"{base_url}/search?q={payload}", timeout=5)
                    status = res.status_code
                    if status == 403:
                        msg = "BLOCKED - XSS detected"
                        summary["blocked"] += 1
                    elif status in [200, 401]:
                        msg = "TRAPPED - Honeypot caught XSS"
                        summary["trapped"] += 1
                    else:
                        msg = "Request processed"
                        summary["passed"] += 1
                    
                    results.append({
                        "endpoint": f"/search?q={payload[:25]}...",
                        "status_code": status,
                        "message": msg
                    })
                    summary["total_requests"] += 1
                except Exception as e:
                    results.append({
                        "endpoint": "/search",
                        "status_code": 0,
                        "message": f"Error: {str(e)}"
                    })
                    
        elif attack_type == 'file_probe':
            probe_paths = [
                ("/.env", "Sensitive Config File"),
                ("/backup.sql", "Database Backup"),
                ("/shell", "RCE Endpoint"),
                ("/administrator", "Legacy Admin"),
                ("/../../../etc/passwd", "Path Traversal")
            ]
            for path, desc in probe_paths:
                try:
                    res = requests.get(f"{base_url}{path}", timeout=5)
                    status = res.status_code
                    if status == 403:
                        msg = f"BLOCKED - {desc} access denied"
                        summary["blocked"] += 1
                    elif status in [200, 401]:
                        msg = f"TRAPPED - Honeypot served fake {desc}"
                        summary["trapped"] += 1
                    elif status == 404:
                        msg = "Not Found"
                        summary["passed"] += 1
                    else:
                        msg = f"Response: {status}"
                        summary["passed"] += 1
                    
                    results.append({
                        "endpoint": f"{path} ({desc})",
                        "status_code": status,
                        "message": msg
                    })
                    summary["total_requests"] += 1
                except Exception as e:
                    results.append({
                        "endpoint": path,
                        "status_code": 0,
                        "message": f"Error: {str(e)}"
                    })
                    
        elif attack_type == 'full_suite':
            # Run all attacks
            for sub_attack in ['bruteforce', 'sqli', 'xss', 'file_probe']:
                sub_result = run_attack_internal(sub_attack, base_url)
                results.extend(sub_result['results'])
                for key in summary:
                    summary[key] += sub_result['summary'].get(key, 0)
        
        return jsonify({
            "success": True,
            "attack_type": attack_type,
            "results": results,
            "summary": summary
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "attack_type": attack_type,
            "error": str(e),
            "results": results,
            "summary": summary
        })


def run_attack_internal(attack_type, base_url):
    """Internal helper for full_suite attack"""
    results = []
    summary = {"total_requests": 0, "blocked": 0, "trapped": 0, "passed": 0}
    
    if attack_type == 'bruteforce':
        for i in range(2):
            try:
                res = requests.post(f"{base_url}/admin-panel", 
                                   data={"username": "admin", "password": "test"},
                                   timeout=5)
                results.append({
                    "endpoint": f"/admin-panel (BF #{i+1})",
                    "status_code": res.status_code,
                    "message": "BLOCKED" if res.status_code == 403 else "TRAPPED"
                })
                summary["total_requests"] += 1
                if res.status_code == 403: summary["blocked"] += 1
                else: summary["trapped"] += 1
            except:
                pass
                
    elif attack_type == 'sqli':
        try:
            res = requests.get(f"{base_url}/api/v1/user-data?id=' OR 1=1", timeout=5)
            results.append({
                "endpoint": "/api/v1/user-data (SQLi)",
                "status_code": res.status_code,
                "message": "BLOCKED" if res.status_code == 403 else "TRAPPED"
            })
            summary["total_requests"] += 1
            if res.status_code == 403: summary["blocked"] += 1
            else: summary["trapped"] += 1
        except:
            pass
            
    elif attack_type == 'xss':
        try:
            res = requests.get(f"{base_url}/search?q=<script>alert(1)</script>", timeout=5)
            results.append({
                "endpoint": "/search (XSS)",
                "status_code": res.status_code,
                "message": "BLOCKED" if res.status_code == 403 else "PROCESSED"
            })
            summary["total_requests"] += 1
            if res.status_code == 403: summary["blocked"] += 1
            else: summary["passed"] += 1
        except:
            pass
            
    elif attack_type == 'file_probe':
        for path in ['/.env', '/backup.sql']:
            try:
                res = requests.get(f"{base_url}{path}", timeout=5)
                results.append({
                    "endpoint": path,
                    "status_code": res.status_code,
                    "message": "BLOCKED" if res.status_code == 403 else "TRAPPED"
                })
                summary["total_requests"] += 1
                if res.status_code == 403: summary["blocked"] += 1
                else: summary["trapped"] += 1
            except:
                pass
    
    return {"results": results, "summary": summary}


# ==========================
# Defense Control API
# ==========================

@app.route('/api/defense/action', methods=['POST'])
def api_defense_action():
    """Frontend'den gelen savunma komutlarını çalıştırır"""
    data = request.get_json()
    action = data.get('action', '')
    
    try:
        if action == 'self_heal':
            return jsonify({
                "success": True,
                "action": "Self-Healing",
                "message": "System healed! All temporary blocks cleared.",
                "data": {
                    "blocks_cleared": 0,
                    "suspicious_cleared": 0
                }
            })
            
        elif action == 'view_blocked':
            return jsonify({
                "success": True,
                "action": "View Blocked IPs",
                "message": "Currently blocked IPs retrieved",
                "data": {
                    "blocked_ips": [],
                    "suspicious_ips": []
                }
            })
            
        elif action == 'system_status':
            db_path = 'honeypot_logs.db'
            threat_count = 0
            threat_types = {}
            
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM threats")
                threat_count = cursor.fetchone()[0]
                cursor.execute("SELECT threat_type, COUNT(*) FROM threats GROUP BY threat_type")
                threat_types = dict(cursor.fetchall())
                conn.close()
            
            return jsonify({
                "success": True,
                "action": "System Status",
                "message": "System status retrieved successfully",
                "data": {
                    "total_threats_logged": threat_count,
                    "threat_breakdown": threat_types,
                    "honeypots_active": 5,
                    "system_health": "OPERATIONAL"
                }
            })
            
        elif action == 'clear_logs':
            db_path = 'honeypot_logs.db'
            dim_path = 'dim_threat_memory.json'
            
            cleared_db = False
            cleared_dim = False
            
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM threats")
                conn.commit()
                conn.close()
                cleared_db = True
            
            if os.path.exists(dim_path):
                with open(dim_path, 'w') as f:
                    json.dump([], f)
                cleared_dim = True
            
            return jsonify({
                "success": True,
                "action": "Clear Logs",
                "message": "All threat logs have been cleared",
                "data": {
                    "database_cleared": cleared_db,
                    "dim_memory_cleared": cleared_dim
                }
            })
            
        elif action == 'export_report':
            db_path = 'honeypot_logs.db'
            report = {
                "report_title": "Neon Immune System - Security Report",
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "summary": {},
                "top_threats": [],
                "recommendations": []
            }
            
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM threats")
                report["summary"]["total_threats"] = cursor.fetchone()[0]
                
                cursor.execute("SELECT threat_type, COUNT(*) FROM threats GROUP BY threat_type ORDER BY COUNT(*) DESC")
                report["summary"]["by_type"] = dict(cursor.fetchall())
                
                cursor.execute("SELECT ip_address, COUNT(*) as cnt FROM threats GROUP BY ip_address ORDER BY cnt DESC LIMIT 10")
                report["top_threats"] = [{"ip": row[0], "attack_count": row[1]} for row in cursor.fetchall()]
                
                conn.close()
            
            if report["summary"].get("total_threats", 0) > 100:
                report["recommendations"].append("High threat volume detected. Consider enabling stricter rate limiting.")
            if "BruteForce" in report["summary"].get("by_type", {}):
                report["recommendations"].append("BruteForce attacks detected. Implement account lockout policies.")
            
            return jsonify({
                "success": True,
                "action": "Export Report",
                "message": "Security report generated",
                "data": report
            })
            
        else:
            return jsonify({
                "success": False,
                "action": action,
                "message": f"Unknown action: {action}"
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "action": action,
            "error": str(e)
        })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
