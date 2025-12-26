import time

class AdaptiveResponseEngine:
    def __init__(self):
        # HAFTA 4 GÜNCELLEMESİ: Self-Healing için yapı değişikliği
        # Eskiden sadece set() idi, şimdi {ip: kilit_acilma_zamani} sözlüğü oldu.
        self.blocked_ips = {} 
        self.suspicious_ips = {} 
        
        # AYARLAR
        self.BLOCK_THRESHOLD = 5   # Bloklanma sınırı
        self.BLOCK_DURATION = 30   # Kaç saniye bloklu kalsın? (Test için kısa tuttuk)

    def analyze_behavior(self, ip_address, risk_score=1):
        """
        Gelen IP'yi analiz eder. Eğer blok süresi dolmuşsa affeder (Self-Healing).
        """
        # 1. SELF-HEALING KONTROLÜ (Kendini İyileştirme)
        if ip_address in self.blocked_ips:
            unlock_time = self.blocked_ips[ip_address]
            
            if time.time() > unlock_time:
                # Süre dolmuş, IP'yi affet
                del self.blocked_ips[ip_address]
                self.suspicious_ips[ip_address] = 0 # Sicilini temizle
                print(f"[SELF-HEALING] 🩹 Timer expired. IP {ip_address} has been UNBLOCKED.")
            else:
                # Süre dolmamış, hala bloklu
                remaining = int(unlock_time - time.time())
                print(f"[BLOCKED] IP {ip_address} is in penalty box for {remaining}s more.")
                return "BLOCK"

        # 2. RİSK PUANLAMA
        current_score = self.suspicious_ips.get(ip_address, 0) + risk_score
        self.suspicious_ips[ip_address] = current_score

        print(f"[ADAPTIVE ENGINE] IP: {ip_address} | Score: {current_score}/{self.BLOCK_THRESHOLD}")

        # 3. KARAR ANI
        if current_score >= self.BLOCK_THRESHOLD:
            # Şu anki zamana blok süresini ekle
            self.blocked_ips[ip_address] = time.time() + self.BLOCK_DURATION
            print(f"[ADAPTIVE ENGINE] ⛔️ THREAT NEUTRALIZED: IP {ip_address} BLOCKED for {self.BLOCK_DURATION}s.")
            return "BLOCK"
        
        return "MONITOR"

    def is_blocked(self, ip_address):
        """Middleware için kontrol fonksiyonu. Süre dolduysa 'Bloklu Değil' der."""
        if ip_address in self.blocked_ips:
            # Kontrol anında süre dolmuş mu bak
            if time.time() > self.blocked_ips[ip_address]:
                del self.blocked_ips[ip_address]
                self.suspicious_ips[ip_address] = 0
                return False # Artık bloklu değil
            return True # Hala bloklu
        return False