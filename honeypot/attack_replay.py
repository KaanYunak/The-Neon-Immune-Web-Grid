import json
import requests
import time

class AttackReplaySystem:
    def __init__(self, log_file="dim_threat_memory.json", target_url="http://127.0.0.1:5000"):
        self.log_file = log_file
        self.target_url = target_url

    def replay_last_attacks(self):
        """Geçmiş saldırıları tekrar oynatır ve sistemin yeni tepkisini ölçer."""
        print("[REPLAY] Loading past threats from Digital Immune Memory...")
        try:
            with open(self.log_file, 'r') as f:
                attacks = json.load(f)
            
            for attack in attacks[-5:]: # Son 5 saldırıyı dene
                print(f"[REPLAY] Replaying {attack['threat_type']} on {attack['target_endpoint']}")
                # Burada simüle edilmiş bir istek gönderilir
                time.sleep(1)
        except Exception as e:
            print(f"[REPLAY] Error: {e}")