# detector.py

"""
BOT VS NORMAL KULLANICI KRİTERLERİ:

1. İstek Hızı (Velocity):
   - Botlar insanüstü hızda arka arkaya istek atar.
   - İnsanlar sayfalar arasında okuma süresi kadar bekler.

2. Kaynak İstekleri:
   - Normal tarayıcı HTML ile birlikte CSS, JS, Favicon ister.
   - Basit botlar sadece HTML'i çeker.

3. Flow (Akış):
   - Botlar direkt /admin gibi uç noktalara atlar.
   - İnsanlar Ana Sayfa -> Link -> Hedef sırasını izler.
"""