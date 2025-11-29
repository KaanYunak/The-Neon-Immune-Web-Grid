class AdaptiveResponseEngine:
    def __init__(self):
        # Gelecekte burası veritabanından config çekecek
        self.blocking_threshold = 80
        self.tarpit_threshold = 50

    def decide_response(self, threat_score, ip_address):
        """
        Tehdit skoruna göre aksiyon kararı verir.
        Score: 0-100 arası bir risk puanı.
        """
        print(f"[ADAPTIVE ENGINE] Analyzing Threat Score: {threat_score} for IP: {ip_address}")

        if threat_score >= self.blocking_threshold:
            return {
                "action": "BLOCK",
                "detail": f"Immediate IP ban initiated for {ip_address}",
                "http_status": 403
            }
        
        elif threat_score >= self.tarpit_threshold:
            return {
                "action": "TARPIT",
                "detail": "Delaying response times to waste attacker resources.",
                "delay_seconds": 3.0,
                "http_status": 200
            }
        
        else:
            return {
                "action": "MONITOR",
                "detail": "Logging activity for further analysis.",
                "http_status": 200
            }

# Basit test (Bu dosya direkt çalıştırılırsa)
if __name__ == "__main__":
    engine = AdaptiveResponseEngine()
    
    # Senaryo 1: Düşük tehdit
    print(engine.decide_response(20, "192.168.1.5"))
    
    # Senaryo 2: Yüksek tehdit (Saldırı)
    print(engine.decide_response(95, "10.0.0.66"))