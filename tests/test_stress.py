import threading
import requests
import time

# Hedef URL (Localhost çalışırken)
URL = "http://127.0.0.1:5000/admin" # Şüpheli bir path

def attack():
    try:
        response = requests.get(URL)
        print(f"Status: {response.status_code}")
    except:
        pass

# 50 tane eş zamanlı istek gönderelim
threads = []
print("Yük testi başlıyor...")
start_time = time.time()

for _ in range(50):
    t = threading.Thread(target=attack)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"Test Bitti. Süre: {time.time() - start_time:.2f} saniye")