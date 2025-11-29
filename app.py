from flask import Flask
# --- Sizin Eklediğiniz Import ---
from honeypot.routes import honeypot_bp
# --- Mehmet'in Eklediği Import ---
from middleware import BehaviorEngineMiddleware

app = Flask(__name__)

# --- MEHMET'İN KODU: Middleware Entegrasyonu ---
# Uygulamayı Behavior Engine ile sarmalıyoruz ki her isteği kontrol edebilsin.
app.wsgi_app = BehaviorEngineMiddleware(app)

# --- SİZİN KODUNUZ: Honeypot Entegrasyonu ---
# Honeypot modülünü ana uygulamaya kaydediyoruz.
app.register_blueprint(honeypot_bp)

@app.route('/')
def index():
    # İkinizin mesajını birleştirdim :)
    return """
    <h1>Güvenli Bölgeye Hoş Geldiniz Haşmetli Baablarım</h1>
    <p>Neon Immune System Active.</p>
    <p>Test için <a href='/admin-panel'>/admin-panel</a> adresine gidebilirsiniz.</p>
    """

if __name__ == '__main__':
    # Debug modu açık, port 5000
    app.run(debug=True, port=5000)