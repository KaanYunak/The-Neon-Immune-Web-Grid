import requests
import time

class AttackSimulator:
    def __init__(self, target_url):
        self.target_url = target_url.rstrip('/')
        print(f"[INFO] Attack Simulator initialized for target: {self.target_url}")

    def run_bruteforce(self, endpoint, username, wordlist):
        """
        Basit Brute-Force simülasyonu.
        Fake Admin paneline sürekli giriş dener.
        """
        full_url = f"{self.target_url}{endpoint}"
        print(f"\n[ATTACK] Starting Brute Force on: {full_url}")
        print(f"[CONFIG] Target User: {username}")
        
        for password in wordlist:
            print(f"  -> Trying password: {password}...", end='', flush=True)
            start_time = time.time()
            
            try:
                # POST isteği atıyoruz (Login denemesi)
                response = requests.post(full_url, data={'username': username, 'password': password})
                elapsed = time.time() - start_time
                
                # Eğer sunucu bizi 1.5 saniyeden fazla bekletiyorsa Honeypot çalışıyor demektir
                if elapsed > 1.5:
                    print(f" [FAILED] (Server delayed response by {elapsed:.2f}s - Tarpit Detected!)")
                else:
                    print(f" [FAILED] Status: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print(" [ERROR] Server down! Make sure app.py is running.")
                break

    def run_sqli_test(self, endpoint):
        """
        SQL Injection (SQLi) simülasyonu.
        API endpoint'ine zararlı karakterler gönderir.
        """
        print(f"\n[ATTACK] Starting SQL Injection Test on: {endpoint}")
        payloads = ["' OR '1'='1", "admin' --", "UNION SELECT 1,2,3"]
        
        for payload in payloads:
            # Payload'ı URL'e ekleyip GET isteği atıyoruz
            target = f"{self.target_url}{endpoint}?id={payload}"
            print(f"  -> Injecting: {payload} ...", end='', flush=True)
            
            try:
                response = requests.get(target)
                
                # Sahte SQL hatasını yakalarsak başarılı sayıyoruz
                if "SQLSyntaxError" in response.text:
                    print(" [SUCCESS] Honeypot triggered fake SQL error!")
                else:
                    print(f" [No Reaction] Status: {response.status_code}")
            except Exception as e:
                print(f" [ERROR] {e}")

if __name__ == "__main__":
    # Localhost'taki sunucumuza saldıracağız
    simulator = AttackSimulator("http://127.0.0.1:5000")
    
    # 1. Senaryo: Admin paneline kaba kuvvet saldırısı
    passwords = ["123456", "password", "admin123", "qwerty"]
    simulator.run_bruteforce("/admin-panel", "admin", passwords)
    
    # 2. Senaryo: API'ye SQL Injection saldırısı
    simulator.run_sqli_test("/api/v1/user-data")