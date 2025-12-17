import requests
import time

class AttackSimulator:
    def __init__(self, target_url):
        self.target_url = target_url.rstrip('/')
        print(f"[INFO] Attack Simulator initialized: {self.target_url}")

    def test_honeypot_diversity(self):
        """Hafta 4: Farklı tuzak tiplerini ve Adaptive Behavior'ı test eder."""
        print("\n[ATTACK] Starting Dynamic Honeypot Diversity Test...")
        
        # Farklı endpointler ve beklenen davranışlar
        scenarios = [
            {"path": "/.env", "name": "Sensitive File Probe", "desc": "Dosya Okuma Saldırısı"},
            {"path": "/backup.sql", "name": "DB Leak Probe", "desc": "Veritabanı Sızıntı Testi"},
            {"path": "/shell", "name": "IoT Command Injection", "desc": "Komut Çalıştırma"},
            {"path": "/random-page-123", "name": "Random 404", "desc": "Normal Hata"}
        ]

        for case in scenarios:
            url = f"{self.target_url}{case['path']}"
            print(f"  -> Testing {case['name']} ({url})...", end='', flush=True)
            try:
                response = requests.get(url)
                
                if response.status_code == 403:
                    print(" [BLOCKED] ⛔ Adaptive Defense triggered!")
                elif response.status_code == 401:
                    print(" [TRAPPED] 🎣 Caught by JSON Trap (401)")
                elif response.status_code == 404:
                    print(" [IGNORED] Standard 404 (Correct behavior for non-traps)")
                elif response.status_code == 200:
                    print(" [TRAPPED] 🎣 Caught by Fake File/HTML Trap")
                else:
                    print(f" [STATUS: {response.status_code}]")
            except Exception as e:
                print(f" [ERROR] {e}")
            
            time.sleep(0.5)

    def run_bruteforce(self):
        print("\n[ATTACK] Quick Brute-Force Check...")
        try:
            # Hızlıca 3-4 istek atıp bloklanmayı kontrol et
            for i in range(4):
                res = requests.post(f"{self.target_url}/admin-panel", data={"u":"admin", "p":"123"})
                if res.status_code == 403:
                    print(f"  -> Request {i+1}: [BLOCKED] ⛔ System locked us out.")
                    return
                print(f"  -> Request {i+1}: {res.status_code}")
        except:
            pass

if __name__ == "__main__":
    sim = AttackSimulator("http://127.0.0.1:5000")
    
    # 1. Çeşitlilik Testi (Yeni Endpointler)
    sim.test_honeypot_diversity()
    
    # 2. Bloklama Testi
    sim.run_bruteforce()