# security/validation_firewall.py

from flask import Request
from typing import Iterable

from .validation import is_suspicious_payload, sanitize_text
from .logging_secure import secure_log


def _iter_request_values(req: Request) -> Iterable[str]:
    """
    Request içindeki string alanların hepsini gez:
    - query string (GET)
    - form body (POST)
    - JSON body
    - raw body
    - headers (User-Agent)
    - path
    """

    # 1) Query string (GET parametreleri)  ✅
    for v in req.args.values():
        if v:
            yield v

    # 2) Form body (POST parametreleri)  ✅
    for v in req.form.values():
        if v:
            yield v

    # 3) JSON body  ✅
    try:
        json_data = req.get_json(silent=True)
        if isinstance(json_data, dict):
            for v in json_data.values():
                if v:
                    yield str(v)
        elif isinstance(json_data, list):
            for item in json_data:
                if item:
                    yield str(item)
    except Exception:
        pass

    # 4) Raw body (fallback)  ✅
    try:
        body = req.get_data(cache=True, as_text=True)
        if body:
            yield body
    except Exception:
        pass

    # 5) Path (/?q=<script> gibi testleri güçlendirir)  ✅
    if req.path:
        yield req.path

    # 6) Basit header taraması (User-Agent vs.)  ✅
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

        low = raw_value.lower()

        # 1) Hard XSS signatures (test için garanti)
        if "<script" in low or "</script" in low or "javascript:" in low:
            secure_log(
                "validation_firewall_block",
                {
                    "path": req.path,
                    "method": req.method,
                    "remote_addr": req.remote_addr,
                    "raw_value": raw_value[:200],
                    "rule": "hard_xss_signature",
                },
            )
            return False

        # 2) RAW payload kontrolü
        if is_suspicious_payload(raw_value):
            secure_log(
                "validation_firewall_block",
                {
                    "path": req.path,
                    "method": req.method,
                    "remote_addr": req.remote_addr,
                    "raw_value": raw_value[:200],
                    "stage": "raw",
                },
            )
            return False

        # 3) Sanitized payload kontrolü
        clean_value = sanitize_text(raw_value)
        if is_suspicious_payload(clean_value):
            secure_log(
                "validation_firewall_block",
                {
                    "path": req.path,
                    "method": req.method,
                    "remote_addr": req.remote_addr,
                    "raw_value": raw_value[:200],
                    "stage": "sanitized",
                },
            )
            return False

    return True

