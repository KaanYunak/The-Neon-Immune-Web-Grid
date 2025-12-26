import unittest
import hashlib
import json
import os
import sys

# --- Mock Sınıflar (Simülasyonlar) ---

class MockValidationFirewall:
    def sanitize_input(self, user_input):
        # Basit XSS temizleme simülasyonu
        if "<script>" in user_input:
            return user_input.replace("<script>", "&lt;script&gt;").replace("</script>", "&lt;/script&gt;")
        return user_input

    def check_sql_injection(self, user_input):
        # Basit SQLi kontrolü
        forbidden_patterns = ["' OR '1'='1", "UNION SELECT", ";--"]
        for pattern in forbidden_patterns:
            if pattern in user_input:
                return False # Bloklandı
        return True # Güvenli
    
    def check_csrf_token(self, token, session_token):
        return token == session_token

class MockSecureLogger:
    def __init__(self, log_file="test_security.log"):
        self.log_file = log_file
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        self.last_hash = "0" * 64

    def log_event(self, message):
        # Log verisini hazırla (Hash hariç)
        log_entry = {"message": message, "previous_hash": self.last_hash}
        
        # Veriyi stringe çevir ve hashle (İÇERİK HASHLEME)
        log_string = json.dumps(log_entry, sort_keys=True)
        current_hash = hashlib.sha256(log_string.encode()).hexdigest()
        
        # Hash'i ekle ve kaydet
        log_entry["current_hash"] = current_hash
        self.last_hash = current_hash
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def verify_integrity(self):
        if not os.path.exists(self.log_file):
            return True, 0
        
        last_hash = "0" * 64
        with open(self.log_file, "r") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                try:
                    entry = json.loads(line)
                    
                    # 1. ZİNCİR KONTROLÜ: Önceki hash tutuyor mu?
                    expected_prev = entry.get("previous_hash")
                    if expected_prev != last_hash:
                        return False, i + 1
                    
                    # 2. İÇERİK KONTROLÜ: Veri değiştirilmiş mi? (YENİ EKLENEN KISIM)
                    stored_hash = entry.get("current_hash")
                    
                    # Hash hesaplamak için 'current_hash' alanını geçici olarak çıkar
                    entry_calc = entry.copy()
                    if "current_hash" in entry_calc:
                        del entry_calc["current_hash"]
                        
                    # Yeniden hash hesapla
                    log_string = json.dumps(entry_calc, sort_keys=True)
                    calculated_hash = hashlib.sha256(log_string.encode()).hexdigest()
                    
                    # Hesaplanan hash ile kayıtlı hash uyuşuyor mu?
                    if calculated_hash != stored_hash:
                        return False, i + 1
                    
                    last_hash = stored_hash
                    
                except Exception:
                    return False, i + 1
                    
        return True, 0

# --- Test Senaryoları ---

class TestSecurityModules(unittest.TestCase):
    
    def setUp(self):
        self.firewall = MockValidationFirewall()
        self.logger = MockSecureLogger()

    def test_sql_injection_blocking(self):
        print("\n[TEST] SQL Injection Denemesi...")
        payload = "' OR '1'='1"
        is_safe = self.firewall.check_sql_injection(payload)
        self.assertFalse(is_safe, "SQL Injection payload'ı engellenmeliydi!")
        print(" -> BAŞARILI: SQLi Payload engellendi.")

    def test_xss_sanitization(self):
        print("\n[TEST] XSS Temizleme...")
        payload = "<script>alert('Hacked')</script>"
        sanitized = self.firewall.sanitize_input(payload)
        self.assertNotIn("<script>", sanitized, "Script tagleri temizlenmeliydi!")
        print(f" -> BAŞARILI: Girdi temizlendi: {sanitized}")

    def test_log_integrity_tampering(self):
        print("\n[TEST] Log Manipülasyonu (Tampering)...")
        # 1. Log oluştur
        self.logger.log_event("User Login")
        self.logger.log_event("Admin Access") # Bu satırı değiştireceğiz
        self.logger.log_event("Logout")
        
        # 2. Dosyayı oku ve 2. satırı değiştir
        with open("test_security.log", "r") as f:
            lines = f.readlines()
        
        # Veriyi bozuyoruz ama hash'i güncellemiyoruz (Saldırgan davranışı)
        original_line = json.loads(lines[1])
        original_line["message"] = "HACKED ENTRY" 
        lines[1] = json.dumps(original_line) + "\n"
        
        with open("test_security.log", "w") as f:
            f.writelines(lines)
            
        # 3. Doğrula
        is_valid, line_no = self.logger.verify_integrity()
        
        # Beklenti: is_valid FALSE olmalı (yani bozulma tespit edilmeli)
        self.assertFalse(is_valid, "HATA: Log içeriği değişti ama sistem fark etmedi!")
        print(f" -> BAŞARILI: Log bozulması {line_no}. satırda tespit edildi.")

    def tearDown(self):
        if os.path.exists("test_security.log"):
            os.remove("test_security.log")

if __name__ == '__main__':
    print("=== TEAM 13 GÜVENLİK TEST OTOMASYONU ===")
    unittest.main()