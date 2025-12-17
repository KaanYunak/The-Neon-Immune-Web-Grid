import sqlite3
import requests
import time
from colorama import Fore, Style, init

# Terminal renklerini başlat
init(autoreset=True)

DB_NAME = "honeypot_logs.db"
TARGET_HOST = "http://127.0.0.1:5000"

def get_unique_attacks():
    """Veritabanındaki benzersiz saldırı yollarını çeker."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Aynı path'i tekrar tekrar çekmemek için DISTINCT kullanıyoruz
        cursor.execute("SELECT DISTINCT threat_type, path, risk_score FROM threats ORDER BY risk_score DESC")
        attacks = cursor.fetchall()
        conn.close()
        return attacks
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Veritabanı okunamadı: {e}")
        return []

def replay_attack(threat_type, path, risk):
    """Saldırıyı sunucuya tekrar gönderir."""
    full_url = f"{TARGET_HOST}{path}"
    print(f"\n{Fore.CYAN}[REPLAYING] {threat_type} -> {full_url} (Orig Risk: {risk})")
    
    try:
        start_time = time.time()
        
        # Admin paneli ise POST, diğerleri GET
        if "admin" in path:
            response = requests.post(full_url, data={'username': 'replay_bot', 'password': '123'}, timeout=5)
        else:
            response = requests.get(full_url, timeout=5)
            
        elapsed = time.time() - start_time
        
        # Analiz
        status_color = Fore.GREEN if response.status_code == 200 else Fore.YELLOW
        if response.status_code == 403: status_color = Fore.RED
        
        print(f"   -> Status: {status_color}{response.status_code}{Style.RESET_ALL} | Time: {elapsed:.2f}s")
        print(f"   -> Server Response: {response.text[:50]}...") # İlk 50 karakter
        
    except requests.exceptions.RequestException as e:
        print(f"   -> {Fore.RED}[FAIL] Bağlantı Hatası: {e}")

if __name__ == "__main__":
    print(f"{Fore.MAGENTA}=== NEON IMMUNE SYSTEM: ATTACK REPLAY MODULE ===")
    print(f"{Fore.WHITE}Veritabanındaki tehditler analiz ediliyor...\n")
    
    attacks = get_unique_attacks()
    
    if not attacks:
        print(f"{Fore.YELLOW}Veritabanında kayıtlı saldırı bulunamadı.")
    else:
        print(f"{Fore.GREEN}{len(attacks)} farklı saldırı senaryosu bulundu. Başlatılıyor...")
        time.sleep(1)
        
        for attack in attacks:
            # attack: (type, path, risk)
            replay_attack(attack[0], attack[1], attack[2])
            time.sleep(0.5) # Çok hızlı boğmamak için bekleme
            
    print(f"\n{Fore.MAGENTA}=== REPLAY COMPLETED ===")