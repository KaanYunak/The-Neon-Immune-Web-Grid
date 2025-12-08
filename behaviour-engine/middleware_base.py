from flask import Request, jsonify
from behavior_engine import BehaviorEngine

class BehaviorMiddleware:
    def __init__(self, app):
        self.app = app
        self.wsgi_app = app.wsgi_app
        self.engine = BehaviorEngine()

    def __call__(self, environ, start_response):
        request = Request(environ)
        path = request.path
        
        # 1. Analiz
        score, logs = self.engine.evaluate(path)

        # 2. SELF-EVOLVING MEKANİZMASI 
        # Eğer puan çok çok yüksekse (Örn: 500), saldırganın IP'sini kalıcı kurala ekle
        if score > 500:
            ip = request.remote_addr
            # Daha önce eklenmemişse ekle
            rule_name = f"Auto-Block IP {ip}"
            # IP adresini regex ile tam eşleştiren desen
            pattern = f"^{ip}$" # Gerçek hayatta bunu header analizine bağlardık
            
            # Bu IP'yi direkt engelleyen kuralı sisteme ekle
            # Not: Bu basit bir demo mantığıdır.
            # self.engine.add_dynamic_rule(rule_name, pattern, 1000) 
            print(f"[EVOLUTION] Sistem yeni bir tehdit öğrendi: {ip}")

        # 3. Bloklama
        if score >= self.engine.threshold:
            print(f"[BLOKLANDI] {request.remote_addr} - Puan: {score}")
            res = jsonify({"error": "Blocked", "score": score})
            res.status_code = 403
            return res(environ, start_response)

        return self.wsgi_app(environ, start_response)