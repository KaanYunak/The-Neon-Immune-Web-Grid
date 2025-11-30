from functools import wraps
from flask import session, redirect, url_for, g
from .logging_secure import secure_log

# Şimdilik sadece demo kullanıcılar
USERS = {
    "user@example.com": {
        "password": "User12345",
        "role": "user",
    },
    "admin@example.com": {
        "password": "Admin12345",
        "role": "admin",
    },
    "sec@example.com": {
        "password": "Sec12345",
        "role": "security",
    },
}

def get_current_user():
    email = session.get("user_email")
    if not email:
        return None
    user = USERS.get(email)
    if user:
        user = {**user, "email": email}
    return user

def login_user(email: str):
    session["user_email"] = email

def logout_user():
    session.pop("user_email", None)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect(url_for("login"))
        g.current_user = user
        return f(*args, **kwargs)
    return wrapper

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                return redirect(url_for("login"))
            if user["role"] not in roles:
                secure_log("access_denied", {
                    "email": session.get("user_email"),
                    "role": user.get("role"),
                    "required_roles": roles,
                })
                return "Access denied", 403
            g.current_user = user
            return f(*args, **kwargs)
        return wrapper
    return decorator
