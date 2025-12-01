from flask import Request, jsonify

# SENİN MODÜLLERİN
from security.validation import is_suspicious_payload
from security.logging_secure import secure_log


class BehaviorEngineMiddleware:
    def __init__(self, app):
        self.app = app
        # Orijinal WSGI uygulamasını sakla
        self.wsgi_app = app.wsgi_app

    def __call__(self, environ, start_response):
        # 1. Flask Request objesi oluştur
        request = Request(environ)

        # 2. Davranış analizini çalıştır
        is_suspicious, score = self.analyze_request(request)

        # 3. Eğer puan threshold'un üstündeyse: logla + blokla
        if is_suspicious:
            secure_log("suspicious_request_blocked", {
                "ip": request.remote_addr,
                "path": request.path,
                "method": request.method,
                "user_agent": str(request.user_agent),
                "query_string": request.query_string.decode("utf-8", errors="ignore"),
                "score": score,
            })

            res = jsonify({
                "error": "Suspicious activity detected",
                "score": score,
            })
            res.status_code = 403
            return res(environ, start_response)

        # 4. Şüpheli değilse isteğin devam etmesine izin ver
        return self.wsgi_app(environ, start_response)

    def analyze_request(self, request):
        """
        Davranış analizi motoru:
        - Path + query string içindeki payload'ı tarar
        - User-Agent'e bakar
        - Basit bir skorlama yapar
        - Skor belli eşiği geçerse is_suspicious = True döner
        """
        score = 0

        # --- 1) Payload analizi (query string + path) ---
        parts = [request.path or ""]
        if request.query_string:
            parts.append(request.query_string.decode("utf-8", errors="ignore"))

        payload_text = " ".join(parts)

        # Senin security.validation içindeki pattern tarayıcı
        if is_suspicious_payload(payload_text):
            score += 80  # SQLi/XSS vs. yakalanırsa yüksek skor

        # --- 2) User-Agent analizi ---
        ua = str(request.user_agent or "").lower()

        # User-Agent yoksa veya çok şüpheli görünüyorsa skor arttır
        if not ua or ua == "none":
            score += 20

        # Bilinen scanner / tool isimleri (örn. sqlmap, nikto vs.)
        SCANNER_KEYWORDS = ["sqlmap", "nikto", "wpscan", "nmap"]
        if any(tool in ua for tool in SCANNER_KEYWORDS):
            score += 50

        # --- 3) Basit rate / parametre yoğunluğu kuralı (şimdilik çok basit) ---
        # Çok fazla query parametresi varsa (örn. tarama gibi)
        if len(request.args) > 10:
            score += 30

        # Threshold'u burada belirliyoruz (şimdilik 100)
        is_suspicious = score >= 100

        # Şüpheli olmasa bile "gözlem" amaçlı loglamak istersen:
        # secure_log("request_observed", {...}) diyebilirsin.

        return is_suspicious, score
