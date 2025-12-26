import sqlite3
import datetime
import os

DB_NAME = "honeypot_logs.db"
REPORT_FILE = "ATTACK_RESULT_REPORT.md"

def generate_markdown_report():
    if not os.path.exists(DB_NAME):
        print("Veritabanı bulunamadı!")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # İstatistikleri Çek
    cursor.execute("SELECT COUNT(*) FROM threats")
    total_attacks = cursor.fetchone()[0]

    cursor.execute("SELECT threat_type, COUNT(*) FROM threats GROUP BY threat_type ORDER BY COUNT(*) DESC")
    type_stats = cursor.fetchall()

    cursor.execute("SELECT ip_address, COUNT(*) FROM threats GROUP BY ip_address ORDER BY COUNT(*) DESC LIMIT 5")
    top_attackers = cursor.fetchall()

    # Raporu Yaz
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# NEON IMMUNE WEB GRID - FINAL GÜVENLİK RAPORU\n")
        f.write(f"**Tarih:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Raporlayan:** Ömer Furkan Tümkaya\n\n")

        f.write("## 1. GENEL ÖZET\n")
        f.write(f"- **Toplam Engellenen Saldırı:** {total_attacks}\n")
        f.write(f"- **Sistem Durumu:** AKTİF ve Stabil\n\n")

        f.write("## 2. TEHDİT DAĞILIMI (Saldırı Tipleri)\n")
        f.write("| Saldırı Tipi | Adet |\n")
        f.write("|---|---|\n")
        for t_type, count in type_stats:
            f.write(f"| {t_type} | {count} |\n")
        f.write("\n")

        f.write("## 3. EN SALDIRGAN IP ADRESLERİ (Top 5)\n")
        for ip, count in top_attackers:
            f.write(f"- **{ip}**: {count} girişim\n")
        
        f.write("\n## 4. SONUÇ VE DEĞERLENDİRME\n")
        f.write("Sistem, SQL Injection, Brute Force ve Hassas Dosya Taraması gibi saldırıları başarıyla tespit etmiş,\n")
        f.write("Adaptive Engine (Davranış Motoru) sayesinde riskli IP adreslerini otomatik olarak karantinaya almıştır.\n")

    conn.close()
    print(f"✅ Rapor başarıyla oluşturuldu: {REPORT_FILE}")

if __name__ == "__main__":
    generate_markdown_report()