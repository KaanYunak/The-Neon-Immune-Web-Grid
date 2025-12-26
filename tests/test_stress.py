import threading
import requests
import time

TARGET_URL = "http://127.0.0.1:5000/admin" 
REQUEST_COUNT = 100
CONCURRENT_THREADS = 10

results = {"200": 0, "403": 0, "ERR": 0}

def attack():
    try:
        response = requests.get(TARGET_URL)
        if response.status_code == 200:
            results["200"] += 1
        elif response.status_code == 403:
            results["403"] += 1
        else:
            results["ERR"] += 1
    except:
        results["ERR"] += 1

def run_test():
    print(f"Test Hedefi: {TARGET_URL}")
    threads = []
    start_time = time.time()

    for i in range(REQUEST_COUNT):
        t = threading.Thread(target=attack)
        threads.append(t)
        t.start()
        
        if len(threads) >= CONCURRENT_THREADS:
            for t in threads:
                t.join()
            threads = []

    for t in threads:
        t.join()

    duration = time.time() - start_time
    print(f"\nSüre: {duration:.2f}sn | Başarılı: {results['200']} | Bloklanan: {results['403']} | Hata: {results['ERR']}")

if __name__ == "__main__":
    run_test()