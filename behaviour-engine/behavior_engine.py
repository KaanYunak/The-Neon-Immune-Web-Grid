import re
import json
import os
import time

class BehaviorEngine:
    def __init__(self, rules_file='behavior-engine/dynamic_rules.json'):
        self.rules_file = rules_file
        self.rules = []
        self.whitelist = []  # YENİ: Whitelist listesi
        self.compiled_rules = []
        self.threshold = 100
        self.last_loaded_time = 0 # YENİ: Son yükleme zamanı
        
        # İlk yükleme
        self.load_rules()

    def load_rules(self):
        """Dosya değişmişse kuralları ve whitelist'i yükler (Caching)."""
        try:
            # Dosyanın son değiştirilme zamanını al
            current_mtime = os.path.getmtime(self.rules_file)
            
            # Eğer dosya değişmediyse tekrar yükleme yapma (Performans Optimizasyonu)
            if current_mtime <= self.last_loaded_time:
                return

            with open(self.rules_file, 'r') as f:
                data = json.load(f)
                self.rules = data.get('rules', [])
                self.whitelist = data.get('whitelist', []) # YENİ
                self.threshold = data.get('threshold', 100)
                
                # Regex Pre-compilation
                self.compiled_rules = []
                for rule in self.rules:
                    self.compiled_rules.append({
                        "name": rule["name"],
                        "score": rule["score"],
                        "pattern": re.compile(rule["pattern"], re.IGNORECASE)
                    })
                
                self.last_loaded_time = current_mtime
                print(f"Kurallar güncellendi (Timestamp: {current_mtime})")
                
        except Exception as e:
            print(f"Kural yükleme hatası: {e}")

    def evaluate(self, request_path, request_body=""):
        # Her istekte dosya değişmiş mi diye kontrol et (Çok hızlıdır)
        self.load_rules()
        
        # YENİ: Whitelist Kontrolü
        # Eğer gelen path whitelist içindeyse direkt 0 puan dön
        for safe_path in self.whitelist:
            if safe_path in request_path:
                return 0, ["Whitelisted path"]

        total_score = 0
        logs = []

        for rule in self.compiled_rules:
            if rule["pattern"].search(request_path) or \
               rule["pattern"].search(str(request_body)):
                total_score += rule["score"]
                logs.append(f"İhlal: {rule['name']} (+{rule['score']})")

        return total_score, logs

    def add_dynamic_rule(self, name, pattern, score):
        """Yeni kural ekler (Stabilizasyon: Duplicate kontrolü)."""
        # Aynı isimde kural varsa ekleme
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
        
        with open(self.rules_file, 'w') as f:
            json.dump(data, f, indent=4)
        
        # Dosya değiştiği için bir sonraki load_rules otomatik algılayacak
        print(f"OTOMATİK KURAL EKLENDİ: {name}")