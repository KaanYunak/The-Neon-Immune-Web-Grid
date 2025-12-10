from flask import Blueprint, render_template, request, jsonify, abort
import time
# Yeni yazdığımız modülleri dahil ediyoruz
from honeypot.dim_logger import DIMLogger
from honeypot.adaptive_response_engine import AdaptiveResponseEngine

honeypot_bp = Blueprint('honeypot', __name__, template_folder='templates')

# Modülleri Başlat (Beyin ve Hafıza Devrede)
dim_logger = DIMLogger()
adaptive_engine = AdaptiveResponseEngine()

# --- GÜVENLİK DUVARI (Middleware) ---
@honeypot_bp.before_request
def check_blocklist():
    """
    Her istekten önce çalışır. 
    Eğer IP adresi Adaptive Engine tarafından bloklanmışsa, kapıdan içeri almaz.
    """
    ip = request.remote_addr
    if adaptive_engine.is_blocked(ip):
        # Saldırgan bloklandıysa 403 Forbidden dön ve bağlantıyı kes
        abort(403, description="Access Denied: Your IP has been flagged by Neon Immune Grid.")

# --- GÖREV: Honeypot Generator (Dinamik Tuzaklar) ---
# Bu yollar gerçekte yok ama saldırgan tarama yaparsa tuzağa düşecek.
generated_fake_endpoints = ['/admin-login', '/secure/db', '/config.php', '/wp-admin', '/backup.sql']

@honeypot_bp.route('/<path:dummy_path>', methods=['GET', 'POST'])
def dynamic_honeypot(dummy_path):
    """
    Tanımsız ama tuzak listesinde olan yollara gelen istekleri yakalar.
    """
    path = f"/{dummy_path}"
    
    # Eğer gidilen yol tuzak listesindeyse:
    if path in generated_fake_endpoints:
        ip = request.remote_addr
        
        # 1. Hafızaya Yaz (DIM)
        dim_logger.log_threat("Scanning/Probing", ip, f"Accessed honeypot: {path}", path)
        
        # 2. Risk Puanını Artır (Adaptive Engine)
        adaptive_engine.analyze_behavior(ip, risk_score=1)
        
        # 3. Sahte bir hata sayfası göster
        return render_template('fake_admin.html', error="System Error: Resource integrity verification failed. Logged.")
    
    # Tuzak değilse normal 404 hatası ver (Normal kullanıcıyı etkileme)
    abort(404)


# --- GÖREV: Fake Admin Panel (Akıllandırılmış Sürüm) ---
@honeypot_bp.route('/admin-panel', methods=['GET', 'POST'])
def fake_admin():
    ip = request.remote_addr
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 1. Logla (DIM Entegrasyonu)
        dim_logger.log_threat("BruteForce", ip, f"User:{username} Pass:{password}", "/admin-panel")
        
        # 2. Analiz Et ve Karar Ver (Adaptive Response)
        # Her yanlış deneme 1 risk puanı ekler.
        action = adaptive_engine.analyze_behavior(ip, risk_score=1)
        
        # 3. Oyalama (Tarpit)
        time.sleep(2) 
        
        # Eğer motor "BLOCK" emri verdiyse sistemi kilitle
        if action == "BLOCK":
            abort(403)

        return render_template('fake_admin.html', error="Invalid credentials. Attempts logged.")
        
    return render_template('fake_admin.html')

# --- GÖREV: Fake DB Endpoint (SQLi Algılama ve Bloklama) ---
@honeypot_bp.route('/api/v1/user-data', methods=['GET'])
def fake_db():
    user_id = request.args.get('id')
    ip = request.remote_addr
    
    # SQL Injection İmzası Kontrolü
    if user_id and ("'" in user_id or "OR" in user_id.upper() or "UNION" in user_id.upper()):
        
        # Logla ve Yüksek Risk Puanı Ver
        dim_logger.log_threat("SQLInjection", ip, f"Payload: {user_id}", "/api/v1/user-data")
        
        # SQL Injection çok ciddi bir suçtur, direkt 3 puan verip bloklayabiliriz.
        adaptive_engine.analyze_behavior(ip, risk_score=3) 

        # Saldırganı kandırmak için sahte MySQL hatası dön
        return jsonify({
            "error": "SQLSyntaxError", 
            "code": 1064,
            "message": "You have an error in your SQL syntax near '" + user_id + "'"
        }), 500

    return jsonify({"status": "ok", "data": "Restricted Access"})