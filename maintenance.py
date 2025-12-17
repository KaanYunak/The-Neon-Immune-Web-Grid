import sqlite3
import requests
import os
import time
from colorama import Fore, Style, init

init(autoreset=True)

DB_NAME = "honeypot_logs.db"
TARGET_URL = "http://127.0.0.1:5000"
MAX_LOG_COUNT = 50 # Test için düşük tuttuk, normalde 10.000 olabilir

def check_server_health():
    """Sunucunun ayakta olup olmadığını kontrol eder."""
    print(f"{Fore.CYAN}[HEALTH] Sunucu kontrol ediliyor...")
    try:
        response = requests.get(TARGET_URL, timeout=3)
        if response.status_code == 200:
            print(f"{Fore.GREEN}   -> Sunucu AKTİF (Ping: {response.elapsed.total_seconds():.3f}s)")
            return True
        else:
            print(f"{Fore.YELLOW}   -> Sunucu çalışıyor ama {response.status_code} döndü.")
            return True
    except:
        print(f"{Fore.RED}   -> KRİTİK: Sunucuya ulaşılamıyor! (Down)")
        return False

def clean_database():
    """Veritabanı şişmişse eski kayıtları temizler."""
    print(f"\n{Fore.CYAN}[DB CLEANUP] Veritabanı boyutu analiz ediliyor...")
    
    if not os.path.exists(DB_NAME):
        print(f"{Fore.RED}   -> Veritabanı dosyası bulunamadı!")
        return

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Toplam kayıt sayısı
        cursor.execute("SELECT COUNT(*) FROM threats")
        count = cursor.fetchone()[0]
        
        print(f"   -> Mevcut Kayıt Sayısı: {count}")
        
        if count > MAX_LOG_COUNT:
            print(f"{Fore.YELLOW}   -> Sınır ({MAX_LOG_COUNT}) aşıldı. Temizlik başlıyor...")
            
            # En eski kayıtları sil, sadece son 10 taneyi bırak
            keep_count = 10
            delete_count = count - keep_count
            
            # SQLite'da en eski kayıtları silmek için subquery
            cursor.execute(f"""
                DELETE FROM threats 
                WHERE id NOT IN (
                    SELECT id FROM threats ORDER BY id DESC LIMIT {keep_count}
                )
            """)
            
            conn.commit()

            # Veritabanı dosyasını fiziksel olarak küçült
            cursor.execute("VACUUM")
            
            
            print(f"{Fore.GREEN}   -> {delete_count} adet eski kayıt silindi. Veritabanı optimize edildi.")
        else:
            print(f"{Fore.GREEN}   -> Veritabanı durumu stabil. Temizliğe gerek yok.")
            
        conn.close()
        
    except Exception as e:
        print(f"{Fore.RED}   -> Veritabanı hatası: {e}")

if __name__ == "__main__":
    print(f"{Fore.MAGENTA}=== NEON IMMUNE SYSTEM: SELF-HEALING MODULE ===\n")
    
    # 1. Sağlık Kontrolü
    server_up = check_server_health()
    
    # 2. Veritabanı Bakımı
    clean_database()
    
    print(f"\n{Fore.MAGENTA}=== MAINTENANCE COMPLETED ===")