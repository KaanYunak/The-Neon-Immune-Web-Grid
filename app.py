from flask import Flask
# Sizin yazdığınız honeypot modülünü çağırıyoruz
from honeypot.routes import honeypot_bp

app = Flask(__name__)

# Honeypot Blueprint'ini ana uygulamaya kaydediyoruz
# url_prefix yok, yani direkt /admin-panel olarak çalışacak
app.register_blueprint(honeypot_bp)

@app.route('/')
def index():
    return "<h1>Neon Immune System Active</h1><p>Go to <a href='/admin-panel'>/admin-panel</a> to test the honeypot.</p>"

if __name__ == '__main__':
    # Debug modu açık, böylece hata yaparsak terminalde görürüz
    app.run(debug=True, port=5000)