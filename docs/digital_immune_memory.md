# Digital Immune Memory (DIM) – Design Document  
The Neon Immune Web Grid

## 1. Purpose and Overview

Digital Immune Memory (DIM), sistemin saldırı geçmişini öğrenerek gelecekteki tehditlere daha akıllı ve hızlı tepki vermesini sağlar.  
Amaç:
- Şüpheli pattern’leri hafızaya kaydetmek
- Aynı saldırganı tekrar tespit edebilmek
- Davranış motoruna (Behavior Engine) risk sinyali üretmek
- Honeypot ve Validation Firewall modüllerine bilgi akışı sağlamak

DIM, klasik log sisteminden farklı olarak **öğrenen**, **gelişen** ve **saldırgan profili oluşturan** bir yapıdır.

---

## 2. Data Model (Memory Structure)

DIM üç ana veri tipini saklar:

### 2.1 Event Records
Her şüpheli veya bloklanan request şu bilgileri içerir:

- `timestamp`
- `ip_address` (maskelenmiş → ör: `192.168.xxx.xxx`)
- `user_id` (yoksa anonim id)
- `endpoint`
- `request_method`
- `input_category` (query/body/header/cookie)
- `pattern_detected` (XSS, SQLi, Bruteforce, PathTraversal…)
- `risk_score` (0–100)
- `action_taken` (allow, sanitize, block, redirect_to_honeypot)

### 2.2 Attacker Profiles
Aynı saldırgan veya aynı IP için oluşturulan konsolide profil:

- toplam saldırı sayısı
- saldırı çeşitleri
- ortalama risk puanı
- tekrar eden pattern’ler
- son aktivite zamanı

### 2.3 Adaptive Defense State
Sistemin kendini duruma göre otomatik sıkılaştırdığı parametreler:

- IP bazlı rate-limit seviyesi
- validation kurallarının dinamik sıkılığı
- honeypot yoğunluğu (redirect oranı)
- session güvenlik seviyeleri (örn. token rotation sıklığı)

---

## 3. Risk Scoring System

DIM, her saldırıya risk puanı verir.  
Örnek puanlama:

| Saldırı Türü | Risk |
|--------------|------|
| Basic XSS (basit script) | 30 |
| Stored XSS denemesi | 70 |
| SQL Injection imzası | 80 |
| Bruteforce login 5+ deneme | 40 |
| Honeypot’a düşme | 95 |
| Command Injection pattern | 100 |

### Ek kurallar:
- Aynı pattern 3 kez gelirse: +20 ek puan  
- Aynı IP 10 dk içinde 5 saldırı: risk → **otomatik 90 alt limit**
- Admin endpoint üzerinde saldırı: risk × 1.4

---

## 4. DIM Workflow

Her request için süreç şu şekilde ilerler:

1. **Validation Firewall** input’u inceler  
2. Eğer şüpheli → DIM’e event gönderilir  
3. DIM event’i işler, risk puanı hesaplar  
4. Profil verileri güncellenir  
5. Behavior Engine’e sinyal gider  
6. Eğer risk ≥ 80 ise:
   - IP temporary ban  
   - session invalidation  
   - honeypot redirect  
   - dynamic firewall tightening

---

## 5. IP Privacy & Masking

DIM hassas kullanıcı verilerini **asla tam olarak saklamaz**.

- IP’ler şu formatta tutulur: `123.45.xxx.xxx`
- Session id’ler hash’lenir (HMAC-SHA256)
- User-agent sadece hash olarak saklanır
- E-mail veya username gibi PII loglanmaz

---

## 6. Storage Backend

DIM verisi üç katmanlı saklanır:

### 6.1 In-Memory Cache (Hız → Anlık tespit)
- Redis / in-memory dict  
- Saldırgan profili için 15–30 dk TTL

### 6.2 Persistent Storage (Kalıcı hafıza)
- JSON / SQLite / PostgreSQL (projeye göre değişir)
- Günlük event kayıtları burada saklanır

### 6.3 Archive (Uzun süreli hafıza)
- 30+ gün geçmiş saldırı kayıtları  
- Analiz ve model iyileştirmeleri için kullanılır  

---

## 7. Integration Points

DIM, projenin diğer modülleriyle güçlü şekilde entegredir:

### 7.1 Validation Firewall
- Algılanan pattern’leri DIM’e gönderir
- DIM'in ürettiği sinyale göre kurallar sıkılaşabilir

### 7.2 Behavior Engine
- DIM’den gelen risk puanını kullanarak davranış puanı hesaplar
- Aynı IP’den gelen saldırıları behavior scoring içine dahil eder

### 7.3 Honeypot Engine
- DIM tarafından yüksek riskli işaretlenen IP’lere otomatik redirect uygular
- Honeypot event’leri DIM’e geri beslenir (feedback loop)

---

## 8. Adaptive Defense Mechanisms

DIM saldırgan davranışına göre sistemi dinamik olarak değiştirir:

- **Firewall Tightening:** Validation limitlerini zorlaştırır  
- **Aggressive Rate-Limiting:** Aynı IP için throttle uygular  
- **Honeypot Amplification:** Saldırganın isteklerinin %80’i honeypot’a gider  
- **Session Degradation:** Şüpheli kullanıcılar için read-only mod  
- **Silent Drop Mode:** Belirli risk seviyesinde request cevapsız bırakılır

---

## 9. Future Enhancements

- Makine öğrenimi ile saldırgan profil analizi
- Zaman serisi anomali tespiti
- Log korelasyonu (aynı saldırganın farklı endpoint’lerdeki izleri)
- DIM → SIEM entegrasyonu
- Otomatik firewall kural üretimi (AI-assisted WAF)

