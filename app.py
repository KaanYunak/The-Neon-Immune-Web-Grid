from flask import Flask, render_template, jsonify
import sqlite3
import json
import os
# --- Sizin Eklediğiniz Import ---
from honeypot.routes import honeypot_bp
# --- Mehmet'in Eklediği Import ---
from middleware import BehaviorEngineMiddleware

app = Flask(__name__)
app.secret_key = 'neon-immune-secret-key-2025'

# --- MEHMET'İN KODU: Middleware Entegrasyonu ---
# Uygulamayı Behavior Engine ile sarmalıyoruz ki her isteği kontrol edebilsin.
app.wsgi_app = BehaviorEngineMiddleware(app)

# --- SİZİN KODUNUZ: Honeypot Entegrasyonu ---
# Honeypot modülünü ana uygulamaya kaydediyoruz.
app.register_blueprint(honeypot_bp)

# =============================================================================
# FRONTEND DASHBOARD ROUTES
# =============================================================================

@app.route('/')
def index():
    """Ana sayfa - Dashboard'a yönlendir"""
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    """Güvenlik Dashboard Sayfası"""
    return render_template('dashboard.html')

@app.route('/api/dashboard/threats')
def api_threats():
    """Dashboard için tehdit verilerini JSON olarak döndür"""
    threats = []
    stats = {}
    top_attackers = []
    blocked_count = 0
    
    # SQLite'dan verileri çek
    db_path = 'honeypot_logs.db'
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Son 50 tehdit
            cursor.execute("""
                SELECT ip_address, threat_type, path, risk_score, timestamp 
                FROM threats 
                ORDER BY id DESC 
                LIMIT 50
            """)
            rows = cursor.fetchall()
            
            for row in rows:
                threats.append({
                    'ip': row[0],
                    'threat_type': row[1],
                    'endpoint': row[2],
                    'risk': row[3],
                    'timestamp': row[4],
                    'payload': ''
                })
            
            # Tehdit istatistikleri
            cursor.execute("""
                SELECT threat_type, COUNT(*) 
                FROM threats 
                GROUP BY threat_type
            """)
            for row in cursor.fetchall():
                stats[row[0]] = row[1]
            
            # Top saldırganlar
            cursor.execute("""
                SELECT ip_address, COUNT(*) as cnt 
                FROM threats 
                GROUP BY ip_address 
                ORDER BY cnt DESC 
                LIMIT 5
            """)
            for row in cursor.fetchall():
                top_attackers.append({'ip': row[0], 'count': row[1]})
            
            conn.close()
        except Exception as e:
            print(f"DB Error: {e}")
    
    # DIM JSON'dan da veri çek (payload bilgisi için)
    dim_path = 'dim_threat_memory.json'
    if os.path.exists(dim_path):
        try:
            with open(dim_path, 'r') as f:
                dim_data = json.load(f)
                
            # Son kayıtların payload'larını eşleştir
            for i, threat in enumerate(threats[:20]):
                for dim in reversed(dim_data):
                    if (dim.get('attacker_ip') == threat['ip'] and 
                        dim.get('target_endpoint') == threat['endpoint']):
                        threats[i]['payload'] = dim.get('payload_captured', '')[:100]
                        break
        except:
            pass
    
    return jsonify({
        'threats': threats,
        'total': len(threats),
        'stats': stats,
        'top_attackers': top_attackers,
        'blocked_count': blocked_count
    })

@app.route('/api/dashboard/status')
def api_status():
    """Sistem durumu"""
    return jsonify({
        'status': 'active',
        'honeypots': 5,
        'health': 98,
        'version': '1.0-beta'
    })

# =============================================================================

if __name__ == '__main__':
    # Debug modu açık, port 5001
    app.run(debug=True, port=5001, host='0.0.0.0', use_reloader=False)