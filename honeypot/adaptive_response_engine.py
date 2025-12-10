class AdaptiveResponseEngine:
    def __init__(self):
        # Geçici Bellek (RAM) - Proje ilerleyince Redis/DB olabilir
        self.blocked_ips = set()       # Kesin bloklananlar (Kara Liste)
        self.suspicious_ips = {}       # {ip_adresi: toplam_ceza_puani}
        
        # AYARLAR
        self.BLOCK_THRESHOLD = 3       # Kaç puan ceza yerse bloklansın?
        self.TARPIT_THRESHOLD = 1      # Kaç puanda yavaşlatma başlasın?

    def analyze_behavior(self, ip_address, risk_score=1):
        """
        Gelen IP'nin geçmiş suçlarını hatırlar, yeni suçu ekler ve kararı verir.
        """
        # 1. Zaten bloklu mu?
        if ip_address in self.blocked_ips:
            return "BLOCK"

        # 2. Suç puanını artır (Birikimli Hafıza)
        current_score = self.suspicious_ips.get(ip_address, 0) + risk_score
        self.suspicious_ips[ip_address] = current_score

        print(f"[ADAPTIVE ENGINE] IP: {ip_address} | Risk Score: {current_score}")

        # 3. Karar Mekanizması
        if current_score >= self.BLOCK_THRESHOLD:
            self.blocked_ips.add(ip_address)
            print(f"[ADAPTIVE ENGINE] ⛔️ THREAT NEUTRALIZED: IP {ip_address} BLOCKED.")
            return "BLOCK"
        
        elif current_score >= self.TARPIT_THRESHOLD:
            return "TARPIT"  # Yavaşlat
        
        return "MONITOR" # Sadece izle

    def is_blocked(self, ip_address):
        """Middleware veya Route kontrolü için yardımcı fonksiyon"""
        return ip_address in self.blocked_ips

    def reset_memory(self):
        """Hafızayı temizlemek için (Self-Healing senaryosu)"""
        self.blocked_ips.clear()
        self.suspicious_ips.clear()
        print("[ADAPTIVE ENGINE] Memory flushed. System healed.")