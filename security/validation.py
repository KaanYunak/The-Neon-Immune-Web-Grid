import re
from markupsafe import escape

EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

def validate_email(value: str) -> bool:
    if not value:
        return False
    if len(value) > 100:
        return False
    return bool(EMAIL_RE.match(value))

def validate_password(value: str) -> bool:
    if not value:
        return False
    if not (8 <= len(value) <= 64):
        return False
    if not re.search(r"[A-Za-z]", value):
        return False
    if not re.search(r"[0-9]", value):
        return False
    return True

def validate_int_id(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9]+", value or ""))

def sanitize_text(value: str) -> str:
    if value is None:
        return ""
    return str(escape(value.strip()))

SUSPICIOUS_PATTERNS = [
    "<script",
    "onerror=",
    "onload=",
    "union select",
    "' or 1=1",
    "\" or 1=1",
    "drop table",
    "insert into",
    "../",
    "<?php",
    "system(",
    "exec(",
]

def is_suspicious_payload(text: str) -> bool:
    if not text:
        return False
    lower = text.lower()
    return any(pat in lower for pat in SUSPICIOUS_PATTERNS)
