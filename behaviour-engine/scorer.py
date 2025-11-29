# scorer.py

"""
DAVRANIŞ PUANLAMA MODELİ ÖNERİSİ:

1. User-Agent Kontrolü:
   - User-Agent yoksa veya şüpheliyse: +20 Puan

2. İstek Hızı (Rate Limiting):
   - 1 saniyede 10'dan fazla istek: +15 Puan (her istek için)

3. Payload Analizi:
   - SQL Injection belirtisi (UNION, SELECT): +50 Puan
   - XSS belirtisi (<script>): +40 Puan

4. Eşik Değer (Threshold):
   - Toplam puan 100'ü geçerse istek bloklanır (403 Forbidden).
"""

def calculate_score(request):
    # İleride buraya kod yazılacak
    pass