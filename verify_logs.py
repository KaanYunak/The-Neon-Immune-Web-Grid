import sqlite3

# Veritabanına bağlan
conn = sqlite3.connect('honeypot_logs.db')
cursor = conn.cursor()

# Verileri çek
cursor.execute("SELECT * FROM threats ORDER BY id DESC LIMIT 5")
rows = cursor.fetchall()

print("\n--- SON 5 SALDIRI KAYDI ---")
if not rows:
    print("Henüz kayıt yok. Simülatörü çalıştırdınız mı?")
else:
    for row in rows:
        # row yapısı: (id, ip, type, path, risk, time)
        print(f"[{row[5]}] 🚨 {row[2]} -> {row[3]} (Risk: {row[4]})")

conn.close()