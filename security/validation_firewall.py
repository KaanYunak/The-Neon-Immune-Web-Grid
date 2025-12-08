# security/validation_firewall.py

from flask import Request
from typing import Iterable

from .validation import is_suspicious_payload, sanitize_text
from .logging_secure import secure_log


def _iter_request_values(req: Request) -> Iterable[str]:
    """
    Request içindeki string alanların hepsini gez:
    - query string
    - form body
    - headers (isteğe bağlı)
    """
    # Query string (GET parametreleri)
    for v in req.args.values():
        yield v

    # Form body (POST parametreleri)
    for v in req.form.values():
        yield v

    # Basit header taraması (User-Agent vs.)
    user_agent = req.headers.get("User-Agent")
    if user_agent:
        yield user_agent


def run_validation_firewall(req: Request) -> bool:
    """
    True dönerse istek güvenli, False dönerse bloklanmalı.
    """
    for raw_value in _iter_request_values(req):
        if not raw_value:
            continue

        # Önce sanitize edelim (html encode vs.)
        clean_value = sanitize_text(raw_value)

        # Ardından şüpheli pattern var mı bak
        if is_suspicious_payload(clean_value):
            secure_log("validation_firewall_block", {
                "path": req.path,
                "method": req.method,
                "remote_addr": req.remote_addr,
                "raw_value": raw_value[:200],  # log'u şişirmemek için kısalt
            })
            return False

    return True
