import re
import json
import os
import time


class BehaviorEngine:
    def __init__(self, rules_file="behavior-engine/dynamic_rules.json"):
        self.rules_file = rules_file
        self.rules = []
        self.whitelist = []          # Whitelisted paths/patterns
        self.compiled_rules = []     # Precompiled regex rules for performance
        self.threshold = 100
        self.last_loaded_time = 0    # Cache: last mtime we loaded

        # Initial load
        self.load_rules()

    def load_rules(self):
        """
        Load rules from JSON only if the file changed (mtime caching),
        and precompile regex patterns for fast evaluation.
        """
        try:
            current_mtime = os.path.getmtime(self.rules_file)

            # If file not changed, do nothing (performance optimization)
            if current_mtime <= self.last_loaded_time:
                return

            with open(self.rules_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.rules = data.get("rules", [])
            self.whitelist = data.get("whitelist", [])
            self.threshold = data.get("threshold", 100)

            # Precompile regex patterns
            self.compiled_rules = []
            for rule in self.rules:
                self.compiled_rules.append({
                    "name": rule["name"],
                    "score": rule["score"],
                    "pattern": re.compile(rule["pattern"], re.IGNORECASE),
                })

            self.last_loaded_time = current_mtime
            # print(f"Rules updated (mtime: {current_mtime})")

        except Exception as e:
            print(f"Rule loading error: {e}")

    def evaluate(self, request_path, request_body=""):
        """
        Evaluate request and return (total_score, logs).
        Whitelisted paths return score 0 immediately.
        """
        # Check if rules file changed (fast)
        self.load_rules()

        # Whitelist bypass
        for safe_path in self.whitelist:
            if safe_path and safe_path in (request_path or ""):
                return 0, ["Whitelisted path"]

        total_score = 0
        logs = []

        body_str = str(request_body) if request_body is not None else ""

        for rule in self.compiled_rules:
            if rule["pattern"].search(request_path or "") or rule["pattern"].search(body_str):
                total_score += rule["score"]
                logs.append(f"Violation: {rule['name']} (+{rule['score']})")

        return total_score, logs

    def add_dynamic_rule(self, name, pattern, score):
        """
        Add a new dynamic rule (with duplicate name protection),
        then persist it while preserving threshold + whitelist.
        """
        # Prevent duplicates by rule name
        for r in self.rules:
            if r.get("name") == name:
                return

        new_rule = {"name": name, "pattern": pattern, "score": score}
        self.rules.append(new_rule)

        data = {
            "threshold": self.threshold,
            "whitelist": self.whitelist,
            "rules": self.rules,
        }

        with open(self.rules_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # Next request will reload due to mtime change
        # print(f"DYNAMIC RULE ADDED: {name}")
