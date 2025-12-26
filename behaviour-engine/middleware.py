from flask import Request, jsonify

class BehaviorEngineMiddleware:
    def __init__(self, app):
        self.app = app
        self.wsgi_app = app.wsgi_app

    def __call__(self, environ, start_response):
        # --- MAJESTELERİNE ÖZEL GEÇİŞ İZNİ (Whitelist) ---
        # Gelen istek 127.0.0.1 (localhost) ise analizi atla ve direkt geçiş ver.
        if environ.get('REMOTE_ADDR') == '127.0.0.1':
            return self.wsgi_app(environ, start_response)
        # -------------------------------------------------

        # 1. Gelen isteği analiz için yakala
        request = Request(environ)
        
        # 2. Analiz Fonksiyonunu Çağır
        is_suspicious, score = self.analyze_request(request)

        # 3. Eğer puan çok yüksekse blokla
        if is_suspicious:
            res = jsonify({'error': 'Suspicious activity detected', 'score': score})
            res.status_code = 403
            return res(environ, start_response)

        # 4. Sorun yoksa isteğin devam etmesine izin ver
        return self.wsgi_app(environ, start_response)

    def analyze_request(self, request):
        # Burası davranış analizi motorumuzun kalbi
        current_score = 0
        
        # Örnek kural: User-Agent yoksa puan ekle
        if not request.user_agent:
            current_score += 20
            
        # Puan 100'ü geçerse True döner (Şu anki basit kuralda 100'ü geçmesi zor, 
        # ama simülatörünüz muhtemelen çok hızlı istek attığı için başka bir kural 
        # veya Flask'ın kendi koruması devreye giriyor olabilir.)
        return (current_score > 100), current_score