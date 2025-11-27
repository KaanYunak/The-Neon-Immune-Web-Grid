import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-change-me-please")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # HTTP ile dev yapıyorsan False, üretimde True
    SESSION_COOKIE_SAMESITE = "Strict"

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)

