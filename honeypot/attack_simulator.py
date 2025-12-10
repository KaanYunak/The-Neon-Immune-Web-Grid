import requests
import time

class AttackSimulator:
    def __init__(self, target_url):
        self.target_url = target_url.rstrip('/')
        print(f"[INFO] Attack Simulator initialized for target: {self.target_url}")

    def run_bruteforce(self, endpoint, username, wordlist):
        """
        Brute-Force simülasyonu.
        Artık 403 (Bloklanma) durumunu da kontrol ediyor.
        """
        full_url = f"{self.target_url}{endpoint}"
        print(f"\n[ATTACK] Starting Brute Force on: {full_url}")
        print(f"[CONFIG] Target User: {username}")
        
        for password in wordlist:
            print(f"  -> Trying password: {password}...", end='', flush=True)
            start_time = time.time()
            
            try:
                # Login denemesi yap
                response = requests.post(full_url, data={'username': username, 'password': password})
                elapsed = time.time() - start_time
                
                # --- YENİ EKLENEN KISIM: BLOK KONTROLÜ ---
                if response.status_code == 403:
                    print(f" [BLOCKED] ⛔️ Server blocked our IP! (Adaptive Defense Triggered)")
                    print(" [INFO] Stopping attack loop as we are banned.")
                    break
                
                # Tarpit Kontrolü
                elif elapsed > 1.5:
                    print(f" [TARPIT] Server delayed response by {elapsed:.2f}s")
                else:
                    print(f" [FAILED] Status: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print(" [ERROR] Server down! Make sure app.py is running.")
                break

    def run_sqli_test(self, endpoint):
        """
        SQL Injection (SQLi) simülasyonu.
        Artık ciddi saldırılarda bloklanmayı da bekliyor.
        """
        print(f"\n[ATTACK] Starting SQL Injection Test on: {endpoint}")
        # Not: Adaptive Engine, SQLi için 3 puan verip direkt bloklayacak şekilde ayarlandı.
        payloads = ["' OR '1'='1", "admin' --", "UNION SELECT 1,2,3"]
        
        for payload in payloads:
            target = f"{self.target_url}{endpoint}?id={payload}"
            print(f"  -> Injecting: {payload} ...", end='', flush=True)
            
            try:
                response = requests.get(target)
                
                if response.status_code == 403:
                     print(f" [BLOCKED] ⛔️ Server detected SQLi and blocked IP!")
                     break

                # Sahte SQL hatasını yakalarsak
                elif "SQLSyntaxError" in response.text:
                    print(" [SUCCESS] Honeypot triggered fake SQL error!")
                else:
                    print(f" [No Reaction] Status: {response.status_code}")
            except Exception as e:
                print(f" [ERROR] {e}")

if __name__ == "__main__":
    # Localhost'taki sunucumuza saldıracağız
    simulator = AttackSimulator("http://127.0.0.1:5000")
    
    # 1. Senaryo: Admin paneline kaba kuvvet saldırısı
    # Listeye 5 şifre koyduk, Threshold 3 olduğu için 4. denemede bloklanmalıyız.
    passwords = ["123456", "password", "admin123", "qwerty", "must_be_blocked"]
    simulator.run_bruteforce("/admin-panel", "admin", passwords)
    
    # 2. Senaryo: Eğer hala bloklanmadıysak SQLi dene
    # (Genelde yukarıda bloklanınca burası da 403 döner)
    simulator.run_sqli_test("/api/v1/user-data")