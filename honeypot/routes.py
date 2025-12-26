from flask import Blueprint, render_template, request, jsonify, abort, Response
import time
# Modülleri Dahil Et
from honeypot.dim_logger import DIMLogger
from honeypot.adaptive_response_engine import AdaptiveResponseEngine
# HAFTA 4 YENİLİĞİ: Tuzak Çeşitliliği
from honeypot.honeypot_types import HONEYPOT_TEMPLATES

# --- VERİTABANI MODÜLÜ ---
from honeypot.database import log_attack_to_db

honeypot_bp = Blueprint('honeypot', __name__, template_folder='templates')

# Modülleri Başlat
dim_logger = DIMLogger()
adaptive_engine = AdaptiveResponseEngine()

# --- GÜVENLİK DUVARI (Middleware) ---
@honeypot_bp.before_request
def check_blocklist():
    """Adaptive Engine tarafından bloklanan IP'leri engeller."""
    ip = request.remote_addr
    
    # --- MAJESTELERİ İÇİN DOKUNULMAZLIK (WHITELIST) ---
    # Eğer gelen sizseniz (localhost), ban listesini kontrol etmeden geçiş verin.
    if ip == "127.0.0.1":
        return None 
    # --------------------------------------------------

    if adaptive_engine.is_blocked(ip):
        abort(403, description="Neon Immune System: Access Denied via Adaptive Defense.")

# --- HAFTA 4: Adaptive & Dynamic Honeypot Behavior ---
@honeypot_bp.route('/<path:dummy_path>', methods=['GET', 'POST'])
def dynamic_honeypot(dummy_path):
    path = f"/{dummy_path}"
    ip = request.remote_addr
    
    # Gelen isteği şablonlarımızla karşılaştırıyoruz
    matched_template = None
    for key, config in HONEYPOT_TEMPLATES.items():
        if path == config['path']:
            matched_template = config
            break
    
    # EĞER BİR TUZAĞA DENK GELDİYSE:
    if matched_template:
        threat_type = matched_template['type']
        risk = matched_template['risk_weight']

        # [YENİ] 1. Veritabanına Kaydet (Kalıcı Hafıza)
        log_attack_to_db(ip, threat_type, path, risk)
        
        # 2. Hafızaya Yaz (DIM)
        dim_logger.log_threat(threat_type, ip, f"Probe on {path}", path)
        
        # 3. Risk Puanı İşle (Adaptive Engine)
        action = adaptive_engine.analyze_behavior(ip, risk_score=risk)
        
        # Sadece gerçek saldırganları blokla, localhost'u test için bloklama
        if action == "BLOCK" and ip != "127.0.0.1":
            abort(403)

        # 4. Uyarlanabilir Yanıt (Adaptive Behavior)
        resp_type = matched_template['response_type']
        content = matched_template['fake_content']

        if resp_type == "json":
            return jsonify(content), 401 
        elif resp_type == "text":
            return Response(content, mimetype='text/plain')
        elif resp_type == "html":
            return render_template(content, error="Legacy System: Migrated.")
            
    # Tuzak değilse normal 404
    abort(404)


# --- GÖREV: Fake Admin Panel ---
@honeypot_bp.route('/admin-panel', methods=['GET', 'POST'])
def fake_admin():
    ip = request.remote_addr
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # [YENİ] Veritabanına Kaydet
        log_attack_to_db(ip, "BruteForce", "/admin-panel", 1)

        dim_logger.log_threat("BruteForce", ip, f"User:{username}", "/admin-panel")
        
        # Brute Force girişimi
        action = adaptive_engine.analyze_behavior(ip, risk_score=1)
        
        time.sleep(2) # Tarpit
        
        if action == "BLOCK" and ip != "127.0.0.1":
            abort(403)

        return render_template('fake_admin.html', error="Invalid credentials. Logged.")
        
    return render_template('fake_admin.html')

# --- GÖREV: Fake DB Endpoint ---
@honeypot_bp.route('/api/v1/user-data', methods=['GET'])
def fake_db():
    user_id = request.args.get('id')
    ip = request.remote_addr
    
    if user_id and ("'" in user_id or "OR" in user_id.upper() or "UNION" in user_id.upper()):
        
        # [YENİ] Veritabanına Kaydet
        log_attack_to_db(ip, "SQLInjection", "/api/v1/user-data", 3)
        
        dim_logger.log_threat("SQLInjection", ip, f"Payload: {user_id}", "/api/v1/user-data")
        
        # SQL Injection kritik
        adaptive_engine.analyze_behavior(ip, risk_score=3) 

        return jsonify({
            "error": "SQLSyntaxError", 
            "code": 1064,
            "message": f"You have an error in your SQL syntax near '{user_id}'"
        }), 500

    return jsonify({"status": "ok", "data": "Restricted Access"})