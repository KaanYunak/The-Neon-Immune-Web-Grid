import re
import json
import os

class BehaviorEngine:
    def __init__(self, rules_file='behavior-engine/dynamic_rules.json'):
        self.rules_file = rules_file
        self.rules = []
        self.threshold = 100
        self.load_rules()

    def load_rules(self):
        """JSON dosyasından kuralları yükler."""
        try:
            with open(self.rules_file, 'r') as f:
                data = json.load(f)
                self.rules = data.get('rules', [])
                self.threshold = data.get('threshold', 100)
                print("Kurallar başarıyla yüklendi.")
        except Exception as e:
            print(f"Kural dosyası okunamadı: {e}")

    def evaluate(self, request_path, request_body=""):
        """İsteği analiz eder ve toplam risk puanını döner."""
        total_score = 0
        logs = []

        # Tüm kuralları tek tek kontrol et
        for rule in self.rules:
            pattern = rule['pattern']
            # Hem URL'de hem de Body'de (varsa) arama yap
            if re.search(pattern, request_path, re.IGNORECASE) or \
               re.search(pattern, str(request_body), re.IGNORECASE):
                
                total_score += rule['score']
                logs.append(f"Kural İhlali: {rule['name']} (+{rule['score']})")

        return total_score, logs