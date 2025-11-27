# Validation Firewall Design – The Neon Immune Web Grid

## 1. Amaç ve Genel Bakış

Validation Firewall, uygulamaya gelen her request’in:
- tipini,
- formatını,
- boyutunu,
- içeriğini

kontrol eden ilk savunma hattıdır.  
Amaç:
- XSS, SQL Injection, Command Injection, Path Traversal gibi saldırıları daha backend’e ulaşmadan kesmek,
- hatalı / beklenmeyen input’u güvenli şekilde reddetmek,
- şüpheli davranışları **Digital Immune Memory (DIM)** ve **Behavior Engine** ile paylaşmaktır.

---

## 2. Kapsam (Scope)

Validation Firewall aşağıdaki noktaları kapsar:

- Login / Register formları
- Parola reset / mail doğrulama istekleri
- Admin panel formları
- Arama / filtreleme endpoint’leri
- API endpoint’leri (JSON body alan tüm istekler)
- Honeypot endpoint’lerine gelen input’lar (saldırı tespiti için loglanır)

Her endpoint için ayrı validation profili tanımlanacaktır.

---

## 3. Pipeline Mimarisi

Her request aşağıdaki aşamalardan geçer:

1. **Input Source Normalization**
   - Query string, form-data, JSON body, headers, cookies tek ortak yapıya çevrilir.
2. **Schema Validation**
   - Zorunlu alanlar var mı?
   - Tipler doğru mu? (string, int, email, uuid, vs.)
   - Minimum / maksimum uzunluklar uygun mu?
3. **Content Validation**
   - Regex bazlı whitelist / blacklist kontrolü
   - Encoding normalizasyonu (UTF-8, HTML entity decode vb.)
4. **Malicious Pattern Detection**
   - XSS, SQLi, RCE gibi imza tabanlı kontroller
   - Bilinen payload listeleriyle karşılaştırma
5. **Decision**
   - Clean → request devam eder
   - Suspicious → log + puan + gerekirse sanitize
   - Malicious → request bloklanır, gerekirse honeypot’a yönlendirilir

---

## 4. Endpoint Bazlı Validation Profilleri

Örnek tablo:

| Endpoint         | Method | Giriş Alanları                            | Zorunlu? | Tip        | Özel Kurallar                          |
|------------------|--------|-------------------------------------------|----------|------------|----------------------------------------|
| `/login`         | POST   | username, password                       | Evet     | string     | username: 3–32 char, password: 8–72    |
| `/register`      | POST   | email, username, password                | Evet     | string     | email: RFC5322, username unique        |
| `/search`        | GET    | q, page                                  | Hayır    | string/int | q max 100 char, page 1–100             |
| `/admin/*`       | ANY    | tüm query/body                            | Evet     | mixed      | sadece admin rolüne izin, sıkı limit   |

Bu profiller JSON/YAML dosyalarında saklanacak (örn. `security/validation_profiles.json`).

---

## 5. Validation Kuralları

### 5.1 Tip Kontrolleri
- int alanları için: sadece `^[0-9]+$`
- float alanları için: `^[0-9]+(\.[0-9]+)?$`
- boolean için: `true/false` veya `0/1`
- enum alanlar: whitelist listesi

### 5.2 Uzunluk ve Boyut Limitleri
- Genel kural:
  - string alanlar: max 255 karakter
  - free-text alanlar: max 2000 karakter
- Dosya upload varsa:
  - max boyut, izin verilen mime-type listesi

### 5.3 XSS Önleme
- `<script>`, `onerror=`, `onload=`, `javascript:` gibi pattern’ler blacklist
- `<` ve `>` karakterlerinin encode edilmesi (context’e göre)
- HTML kabul edilen alanlar için safe allowlist tag’ler (örn. `<b>`, `<i>`, `<a>`)

### 5.4 SQL Injection Önleme
- `' OR 1=1`, `UNION SELECT`, `--`, `/* */` gibi pattern’ler
- DB erişiminde kesinlikle **prepared statement / parametrized query** kullanımı
- Numeric alanlarda tek tırnak, noktalı virgül, comment karakterleri yasak

---

## 6. Hata ve Response Politikası

- Validasyon hatası → **400 Bad Request** veya **422 Unprocessable Entity**
- Response body:
  - Kullanıcıya spesifik payload içeriğini sızdırmaz
  - “Invalid input” tarzı genel mesaj + alan bazlı sade hata bilgisi
- Malicious input tespitinde:
  - Kullanıcıya genel hata mesajı
  - Detaylar sadece loglarda / DIM’de tutulur

---

## 7. Logging & Digital Immune Memory Entegrasyonu

Validation Firewall, aşağıdaki durumlarda log üretir:

- Şüpheli ama bloklanmamış (= low/medium risk) input
- Açıkça saldırı içeren ve bloklanmış high risk input
- Aynı IP / user’dan gelen tekrar eden pattern’ler

Log kayıtları DIM’e şu alanlarla gönderilir:

- timestamp
- user_id (varsa) / anonim id
- IP adresi (maskelenmiş)
- endpoint
- input türü (query/body/header)
- algılanan pattern (örn. `XSS`, `SQLi`, `Bruteforce`)
- alınan aksiyon (allow / sanitize / block / redirect_to_honeypot)

DIM bu veriyi kullanarak:
- Aynı saldırgan için risk puanını artırır
- Behavior Engine’e “bu kullanıcı şüpheli” sinyali gönderir

---

## 8. Genişletilebilirlik

- Validation kuralları **koddan bağımsız config dosyalarında** tutulacak.
- Yeni endpoint eklendiğinde:
  - Sadece profile dosyasına yeni entry eklenmesi yeterli
- Orta vadede:
  - Behavior Engine skoruna göre dinamik olarak kurallar sıkılaştırılabilir
  - Örn: Aynı IP’den şüpheli istekte rate-limit otomatik düşürülür

