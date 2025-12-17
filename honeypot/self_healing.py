import os
import time

class SelfHealingEngine:
    def __init__(self, engine_instance):
        self.engine = engine_instance

    def auto_flush_blocklist(self):
        """Blok listesini periyodik olarak temizler (Kendi kendini iyileştirme)."""
        print("[SELF-HEALING] Checking system health...")
        if len(self.engine.blocked_ips) > 0:
            self.engine.blocked_ips.clear()
            print("[SELF-HEALING] Blocklist flushed to prevent false positives.")
            return True
        return False

    def clean_old_logs(self, log_file="dim_threat_memory.json"):
        """Log dosyası çok büyüdüğünde budama yapar."""
        if os.path.exists(log_file) and os.path.getsize(log_file) > 1024 * 1024: # 1MB üstü
            os.rename(log_file, f"{log_file}.bak")
            print("[SELF-HEALING] Logs rotated due to size.")