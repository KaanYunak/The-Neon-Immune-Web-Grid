import re
import json
import os
import time

class BehaviorEngine:
    def __init__(self, rules_file='behavior-engine/dynamic_rules.json'):
        self.rules_file = rules_file
        self.rules = []
        self.whitelist = []
        self.compiled_rules = []
        self.threshold = 100
        self.last_loaded_time = 0
        self.load_rules()

    def load_rules(self):
        try:
            if not os.path.exists(self.rules_file):
                return

            current_mtime = os.path.getmtime(self.rules_file)
            if current_mtime <= self.last_loaded_time:
                return

            with open(self.rules_file, 'r') as f:
                data = json.load(f)
                self.rules = data.get('rules', [])
                self.whitelist = data.get('whitelist', [])
                self.threshold = data.get('threshold', 100)
                
                self.compiled_rules = []
                for rule in self.rules:
                    try:
                        self.compiled_rules.append({
                            "name": rule["name"],
                            "score": rule["score"],
                            "pattern": re.compile(rule["pattern"], re.IGNORECASE)
                        })
                    except re.error:
                        pass

                self.last_loaded_time = current_mtime
                
        except Exception:
            pass

    def evaluate(self, request_path, request_body=""):
        self.load_rules()
        
        for safe_path in self.whitelist:
            if safe_path in request_path:
                return 0, ["Whitelisted"]

        total_score = 0
        logs = []

        for rule in self.compiled_rules:
            if rule["pattern"].search(request_path) or \
               rule["pattern"].search(str(request_body)):
                total_score += rule["score"]
                logs.append(f"{rule['name']}")

        return total_score, logs

    def add_dynamic_rule(self, name, pattern, score):
        for r in self.rules:
            if r["name"] == name:
                return

        new_rule = {"name": name, "pattern": pattern, "score": score}
        self.rules.append(new_rule)
        
        data = {
            "threshold": self.threshold, 
            "whitelist": self.whitelist, 
            "rules": self.rules
        }
        
        try:
            with open(self.rules_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass