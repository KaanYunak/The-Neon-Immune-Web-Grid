from flask import Flask
from middleware import BehaviorEngineMiddleware

app = Flask(__name__)
# Middleware'i uygulamaya entegre et
app.wsgi_app = BehaviorEngineMiddleware(app)

@app.route('/')
def index():
    return "Güvenli Bölgeye Hoş Geldiniz Haşmetli Baablarım"