import secrets
from flask import session

def generate_csrf_token() -> str:
    token = secrets.token_hex(16)
    session["csrf_token"] = token
    return token

def validate_csrf(token_from_form: str) -> bool:
    token = session.get("csrf_token")
    if not token or not token_from_form:
        return False
    return secrets.compare_digest(token, token_from_form)
