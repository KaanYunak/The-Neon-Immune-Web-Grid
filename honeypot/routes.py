from flask import Blueprint, render_template, request, jsonify
import time

# Blueprint tanımlaması
honeypot_bp = Blueprint('honeypot', __name__, template_folder='templates')

# --- GÖREV: Fake Admin Panel ---
@honeypot_bp.route('/admin-panel', methods=['GET', 'POST'])
def fake_admin():
    if request.method == 'POST':
        # Saldırgan verisini burada yakalıyoruz
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Loglama simülasyonu (İleride veritabanına yazılacak)
        print(f"[HONEYPOT ALERT] Login Attempt -> User: {username} | Pass: {password}")
        
        # Oyalama taktiği (2 saniye gecikme - Tarpit)
        time.sleep(2)
        return render_template('fake_admin.html', error="Connection timeout. Please try again.")
        
    return render_template('fake_admin.html')

# --- GÖREV: Fake DB Endpoint (SQLi Yemi) ---
@honeypot_bp.route('/api/v1/user-data', methods=['GET'])
def fake_db():
    user_id = request.args.get('id')
    
    # Basit bir SQLi kontrolü
    if user_id and ("'" in user_id or "OR" in user_id.upper()):
        return jsonify({
            "error": "SQLSyntaxError", 
            "code": 1064,
            "message": "You have an error in your SQL syntax near '" + user_id + "'"
        }), 500

    return jsonify({"status": "ok", "data": "No sensitive data here."})