from flask import Request, jsonify

class BehaviorEngineMiddleware:
    def __init__(self, app):
        self.app = app
        # WSGI uygulamasını sarmalıyoruz
        self.wsgi_app = app.wsgi_app

    def __call__(self, environ, start_response):
        # 1. Gelen isteği analiz için yakala
        request = Request(environ)
        
        # 2. Analiz Fonksiyonunu Çağır (İleride içini dolduracağız)
        is_suspicious, score = self.analyze_request(request)

        # 3. Eğer puan çok yüksekse blokla
        if is_suspicious:
            res = jsonify({'error': 'Suspicious activity detected', 'score': score})
            res.status_code = 403
            return res(environ, start_response)

        # 4. Sorun yoksa isteğin devam etmesine izin ver
        return self.wsgi_app(environ, start_response)

    def analyze_request(self, request):
        # Burası davranış analizi motorumuzun kalbi olacak
        # Şimdilik dummy (boş) bir dönüş yapıyoruz
        current_score = 0
        # Örnek: User-Agent kontrolü (Basit bir kural)
        if not request.user_agent:
            current_score += 20
            
        return (current_score > 100), current_score