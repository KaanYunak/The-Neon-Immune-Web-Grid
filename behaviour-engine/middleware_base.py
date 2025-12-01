from flask import Request, jsonify
# DİKKAT: Burada yazdığımız motoru import ediyoruz
from behavior_engine import BehaviorEngine 

class BehaviorMiddleware:
    def __init__(self, app):
        self.app = app
        self.wsgi_app = app.wsgi_app
        # Motoru başlatıyoruz
        self.engine = BehaviorEngine()

    def __call__(self, environ, start_response):
        # 1. Gelen isteği yakala
        request = Request(environ)
        
        # 2. Analiz Yap (Path üzerinden)
        path = request.path
        # İleride body analizi de eklenebilir: request.get_data()
        score, logs = self.engine.evaluate(path)

        # 3. Loglama (Test amaçlı konsola basıyoruz)
        if score > 0:
            print(f"[GÜVENLİK UYARISI] IP: {request.remote_addr} | Puan: {score} | Detay: {logs}")

        # 4. Engelleme (Threshold kontrolü)
        if score >= self.engine.threshold:
            print(f"[BLOKLANDI] {request.remote_addr} eşik değeri ({self.engine.threshold}) aştı!")
            
            response = jsonify({
                "error": "Suspicious behavior detected", 
                "score": score,
                "details": logs # İsteğe bağlı: detayları saldırgana göstermek istemeyebilirsiniz
            })
            response.status_code = 403
            return response(environ, start_response)

        # 5. Sorun yoksa isteğin devam etmesine izin ver
        return self.wsgi_app(environ, start_response)