import json
import datetime
import os

class DIMLogger:
    def __init__(self, log_file="dim_threat_memory.json"):
        self.log_file = log_file
        # Log dosyası yoksa oluştur (boş liste olarak)
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)

    def log_threat(self, threat_type, ip_address, payload, endpoint):
        """
        Tehdit verisini Digital Immune Memory (DIM) formatına uygun kaydeder.
        """
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "module": "HONEYPOT",
            "threat_type": threat_type,  # Örn: SQLi, BruteForce
            "attacker_ip": ip_address,
            "target_endpoint": endpoint,
            "payload_captured": payload,
            "severity": "HIGH"
        }

        # Mevcut logları oku, yenisini ekle, kaydet
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logs = []

        logs.append(log_entry)

        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=4)
            
        print(f"[DIM LOG] Threat recorded: {threat_type} from {ip_address}")