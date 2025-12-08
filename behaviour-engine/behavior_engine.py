import re
import json
import time

class BehaviorEngine:
    def __init__(self, rules_file='behavior-engine/dynamic_rules.json'):
        self.rules_file = rules_file
        self.rules = []
        self.compiled_rules = [] # Hız için derlenmiş kurallar burada tutulacak
        self.threshold = 100
        self.load_rules()

    def load_rules(self):
        """JSON'dan kuralları yükler ve Regex'leri derler (Optimize eder)."""
        try:
            with open(self.rules_file, 'r') as f:
                data = json.load(f)
                self.rules = data.get('rules', [])
                self.threshold = data.get('threshold', 100)
                
                # OPTİMİZASYON: Desenleri önceden derliyoruz
                self.compiled_rules = []
                for rule in self.rules:
                    self.compiled_rules.append({
                        "name": rule["name"],
                        "score": rule["score"],
                        "pattern": re.compile(rule["pattern"], re.IGNORECASE) # Derlenmiş obje
                    })
                print("Kurallar yüklendi ve optimize edildi.")
        except Exception as e:
            print(f"Kural hatası: {e}")

    def evaluate(self, request_path, request_body=""):
        total_score = 0
        logs = []

        # Artık derlenmiş kurallar üzerinden hızlıca geçiyoruz
        for rule in self.compiled_rules:
            # Derlenmiş regex objesini kullanıyoruz (.search metodu)
            if rule["pattern"].search(request_path) or \
               rule["pattern"].search(str(request_body)):
                
                total_score += rule["score"]
                logs.append(f"İhlal: {rule['name']} (+{rule['score']})")

        return total_score, logs

    # Self-Evolving Mekanizması İçin Yeni Fonksiyon
    def add_dynamic_rule(self, name, pattern, score):
        """Yeni bir tehdit algılandığında kural listesine ekler ve dosyaya yazar."""
        new_rule = {"name": name, "pattern": pattern, "score": score}
        self.rules.append(new_rule)
        
        # Dosyayı güncelle
        data = {"threshold": self.threshold, "rules": self.rules}
        with open(self.rules_file, 'w') as f:
            json.dump(data, f, indent=4)
        
        # Hafızadaki kuralları yenile
        self.load_rules()
        print(f"YENİ KURAL EKLENDİ: {name}")