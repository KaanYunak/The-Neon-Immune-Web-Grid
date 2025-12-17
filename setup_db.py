# setup_db.py
from honeypot.database import init_db

if __name__ == "__main__":
    print("Veritabanı kurulumu başlatılıyor...")
    init_db()
    print("✅ BAŞARILI: 'threats' tablosu oluşturuldu.")