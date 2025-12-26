import sqlite3
import datetime

# Veritabanı dosyasının adı
DB_NAME = "honeypot_logs.db"

def init_db():
    """Veritabanı ve tablo yoksa oluşturur."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Saldırıları tutacak tabloyu oluşturuyoruz
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS threats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            threat_type TEXT NOT NULL,
            path TEXT,
            risk_score INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"[DATABASE] System initialized: {DB_NAME}")

def log_attack_to_db(ip, threat_type, path, risk_score):
    """Yakalanan saldırıyı veritabanına yazar."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO threats (ip_address, threat_type, path, risk_score)
        VALUES (?, ?, ?, ?)
    ''', (ip, threat_type, path, risk_score))
    
    conn.commit()
    conn.close()