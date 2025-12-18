# behavior_engine.py
import json
import os
import re
import time
from typing import Dict, List, Tuple


POLICY_FILE = os.path.join("security", "policy_store.json")

DEFAULT_POLICY = {
    "whitelist_paths": ["/", "/login", "/logout", "/dashboard/user", "/dashboard/admin"],
    "blacklist_ips": [],
    "blocked_user_agents": [],
    "suspicious_path_patterns": [
        r"(?i)\.\./",                 # path traversal
        r"(?i)<script",               # XSS-ish
        r"(?i)union\s+select",        # SQLi-ish
        r"(?i)or\s+1=1",              # SQLi-ish
    ],
}

def _load_policy() -> Dict:
    if not os.path.exists(POLICY_FILE):
        os.makedirs(os.path.dirname(POLICY_FILE), exist_ok=True)
        with open(POLICY_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_POLICY, f, indent=2, ensure_ascii=False)
        return DEFAULT_POLICY

    with open(POLICY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


class BehaviorEngine:
    """
    Simple, stable scoring engine for Week 4:
    - whitelist paths => score 0
    - blacklist IP => very high score => block
    - suspicious path regex => adds score
    - bad UA tokens => adds score
    """
    def __init__(self):
        self.threshold = 100
        self._policy = _load_policy()
        self._compiled = [re.compile(p) for p in self._policy.get("suspicious_path_patterns", [])]
        self._ua_blocks = [s.lower() for s in self._policy.get("blocked_user_agents", [])]
        self._last_reload = time.time()

    def reload_if_needed(self, ttl_seconds: int = 3):
        # lightweight hot-reload
        now = time.time()
        if now - self._last_reload < ttl_seconds:
            return
        self._policy = _load_policy()
        self._compiled = [re.compile(p) for p in self._policy.get("suspicious_path_patterns", [])]
        self._ua_blocks = [s.lower() for s in self._policy.get("blocked_user_agents", [])]
        self._last_reload = now

    def evaluate(self, *, path: str, ip: str, user_agent: str, query: str, body: str) -> Tuple[int, List[str]]:
        self.reload_if_needed()

        reasons: List[str] = []

        # whitelist
        if path in self._policy.get("whitelist_paths", []):
            return 0, ["whitelist_path"]

        # blacklist IP
        if ip in self._policy.get("blacklist_ips", []):
            return 1000, ["blacklist_ip"]

        score = 0

        # suspicious path patterns
        for rx in self._compiled:
            if rx.search(path) or rx.search(query) or rx.search(body):
                score += 60
                reasons.append(f"pattern:{rx.pattern}")

        # blocked UA tokens
        ua_l = (user_agent or "").lower()
        for tok in self._ua_blocks:
            if tok and tok in ua_l:
                score += 80
                reasons.append(f"ua_block:{tok}")

        # mild signal
        if len(query) > 200:
            score += 20
            reasons.append("long_query")

        return score, reasons
