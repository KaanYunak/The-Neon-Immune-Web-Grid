# security/bruteforce_protection.py

import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple, Optional

# Ayarlar
MAX_ATTEMPTS = 5               # kaç başarısız deneme?
WINDOW_SECONDS = 10 * 60       # bu kadar saniye içinde
BLOCK_SECONDS = 5 * 60         # blok süresi

# "identifier" = ip + email kombinasyonu gibi bir şey olacak
_failed_attempts: Dict[str, Deque[float]] = defaultdict(deque)
_blocked_until: Dict[str, float] = {}


def _now() -> float:
    return time.time()


def register_failed_attempt(identifier: str) -> None:
    """Başarısız login denemesini kaydet."""
    ts = _now()
    attempts = _failed_attempts[identifier]

    # Eski kayıtları temizle
    while attempts and ts - attempts[0] > WINDOW_SECONDS:
        attempts.popleft()

    attempts.append(ts)

    if len(attempts) >= MAX_ATTEMPTS:
        _blocked_until[identifier] = ts + BLOCK_SECONDS


def reset_attempts(identifier: str) -> None:
    """Başarılı login olduğunda temizle."""
    _failed_attempts.pop(identifier, None)
    _blocked_until.pop(identifier, None)


def is_blocked(identifier: str) -> bool:
    """Şu anda blokta mı?"""
    ts = _now()
    until = _blocked_until.get(identifier)
    if not until:
        return False
    if ts >= until:
        # blok süresi dolmuş, temizle
        reset_attempts(identifier)
        return False
    return True


def get_retry_after(identifier: str) -> Optional[int]:
    """Kalan blok süresini saniye olarak döner (ya da None)."""
    until = _blocked_until.get(identifier)
    if not until:
        return None
    remaining = int(until - _now())
    return remaining if remaining > 0 else None
