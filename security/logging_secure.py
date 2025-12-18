import json
import hashlib
import os
import time
from typing import Dict, Any, Optional


LOG_FILE = "security.log"
CHAIN_FILE = "security.log.hash"

def _get_last_hash() -> str:
    if not os.path.exists(CHAIN_FILE):
        return "0"
    with open(CHAIN_FILE, "r", encoding="utf-8") as f:
        return f.read().strip() or "0"

def _store_last_hash(h: str) -> None:
    with open(CHAIN_FILE, "w", encoding="utf-8") as f:
        f.write(h)

def secure_log(
    event_type: str,
    details: Dict[str, Any],
    level: str = "INFO",
    ip: Optional[str] = None,
    path: Optional[str] = None,
    user: Optional[str] = None,
    session_id: Optional[str] = None,

) -> None:
    # details içine meta bilgileri ekle (varsa)
    enriched_details = dict(details or {})
    if level: enriched_details["level"] = level
    if ip: enriched_details["ip"] = ip
    if path: enriched_details["path"] = path
    if user: enriched_details["user"] = user
    if session_id: enriched_details["session_id"] = session_id

    entry = {
        "ts": time.time(),
        "event": event_type,
        "details": enriched_details,
    }

    prev_hash = _get_last_hash()
    data = json.dumps(entry, sort_keys=True, ensure_ascii=False)
    current_hash = hashlib.sha256((prev_hash + data).encode("utf-8")).hexdigest()

    line = f"{data}|{current_hash}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)

    _store_last_hash(current_hash)
