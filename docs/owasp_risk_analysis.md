# OWASP Top 10 – Project Risk Analysis  
**The Neon Immune Web Grid – Security & Scripting Languages Project**  
**Author:** Kaan Yunak  
**Scope:** Proje mimarisi için OWASP Top 10 uyumluluğuna göre risk değerlendirme dokümanı.  

---

# 🌐 1. A01 – Broken Access Control

## Risk Açıklaması
Kullanıcı rolleri (normal user, admin) yanlış yönetildiğinde hassas endpoint’lere yetkisiz erişim sağlanabilir.

## Projede Nasıl Ortaya Çıkabilir?
- `/admin/*` endpoint’lerinin sadece URL temelli korunması  
- Honeypot admin paneline yanlış yönlendirme  
- DIM risk profili göz ardı edilirse role escalation

## Risk Seviyesi  
**High**

## Etkilenen Modüller  
- Validation Firewall  
- Honeypot Engine  
- Behavior Engine  

## Mitigasyon
- Rol tabanlı (RBAC) ve attribute-based control (ABAC) kuralları  
- Tüm admin route'larına güvenli authorization decorator  
- DIM risk ≥ 80 olduğunda otomatik access downgrade  
- Doğrudan ID tabanlı erişim (IDOR) testleri

---

# 🌐 2. A02 – Cryptographic Failures

## Risk Açıklaması
Yanlış anahtar yönetimi, zayıf hash fonksiyonları veya HTTPS kullanılmaması durumunda hassas veriler tehlikeye girer.

## Projede Nasıl Ortaya Çıkabilir?
- `SECRET_KEY` environment variable yerine sabit string olursa  
- Session cookie → HTTPS olmadan Secure flag eksik  
- DIM içinde hash’lenmeden IP kayıt edilmesi

## Risk Seviyesi  
**Medium**

## Etkilenen Modüller  
- Flask Backend  
- DIM  
- Session Security

## Mitigasyon
- Üretimde SECRET_KEY = 32+ byte random  
- SESSION_COOKIE_SECURE = True  
- IP adresleri maskelenerek saklanmalı  
- Tüm tokenlar HMAC-SHA256 ile imzalanmalı

---

# 🌐 3. A03 – Injection (XSS, SQLi, Command Injection)

## Risk Açıklaması
Kullanıcı tarafından sağlanan input işlenmeden backend’e girerse injection saldırıları yapılabilir.

## Projede Nasıl Ortaya Çıkabilir?
- Arama endpoint’inde filtrelenmemiş `q` parametresi  
- XSS payloadlarının Validation Firewall’dan kaçması  
- Test amaçlı honeypot DB endpoint’lerinin açık kalması  

## Risk Seviyesi  
**Critical**

## Etkilenen Modüller  
- Validation Firewall  
- Behavior Engine  
- DIM  
- Honeypot Engine  

## Mitigasyon
- Tüm endpoint’lerde whitelist validation  
- XSS regex imzaları + encoding  
- SQL erişimi için sadece parametrized queries  
- Honeypot’ın gerçek DB ile bağlantısı olmamalı  
- DIM’e injection pattern algılandığında risk ≥ 80

---

# 🌐 4. A04 – Insecure Design

## Risk Açıklaması
Sistem bileşenlerinin tasarımında güvenlik prensiplerinin düşünülmemesi.

## Projede Nasıl Ortaya Çıkabilir?
- Honeypot → saldırganın gerçek sisteme geri yönlenmesi  
- Behavior Engine kurallarının statik kalması  
- DIM risk sinyalinin kullanılmaması  
- Validation Firewall’un bypass edilebilir durumda olması

## Risk Seviyesi  
**High**

## Modüller
- Tüm modüller (Firewall, DIM, Honeypot, BE)

## Mitigasyon
- Secure by Design prensipleri  
- Minimum yetki (least privilege)  
- Input validation pipeline  
- Merkezi log + DIM correlation  
- Red-team test scriptleri

---

# 🌐 5. A05 – Security Misconfiguration

## Risk Açıklaması
Yanlış ayar, eksik güvenlik header’ı, debug açıkları saldırıya kapı açar.

## Projede Nasıl Ortaya Çıkabilir?
- Flask debug mode’un yanlışlıkla prod’da açık bırakılması  
- CORS’un herkese açık olması  
- Security header eksikliği  
- Honeypot’ın yanlışlıkla gerçek admin panelinin yerine deploy edilmesi

## Risk Seviyesi  
**Medium**

## Mitigasyon
- Debug = False (prod)  
- X-Frame-Options, X-Content-Type, CSP header eklenmeli  
- Production .env dosyası  
- Container/VM deployment’larında hardening

---

# 🌐 6. A06 – Vulnerable and Outdated Components

## Risk Açıklaması
Framework veya dependency güncel değilse exploit edilebilir.

## Projede Nasıl Ortaya Çıkabilir?
- Flask eski sürüm  
- Werkzeug/Jinja zafiyetleri  
- Python package lock tutulmaması  
- Honeypot scriptlerinde eski 3rd party kodlar

## Risk Seviyesi  
**Medium**

## Mitigasyon
- `pip-audit` entegrasyonu  
- `requirements.txt` kilitleme  
- Haftalık dependency taraması  
- Docker kullanılırsa image scanning

---

# 🌐 7. A07 – Identification & Authentication Failures

## Risk Açıklaması
Zayıf login, brute force önlemi olmaması, session fixation.

## Projede Nasıl Ortaya Çıkabilir?
- Login rate-limit yoksa brute force geçebilir  
- Session ID rotation yapılmazsa fixation  
- Honeypot login sayfasının gerçek login ile karışması  

## Risk Seviyesi  
**High**

## Mitigasyon
- Rate limit (örn. 5 deneme / 1 dakika)  
- Token rotation on login  
- DIM → brute force tespiti → IP ban  
- Session timeout 15 min

---

# 🌐 8. A08 – Software & Data Integrity Failures

## Risk Açıklaması
Güvenilmeyen kod veya veri, sistem modüllerini manipüle edebilir.

## Projede Nasıl Ortaya Çıkabilir?
- Dynamic rules (behavior engine) dışarıdan manipüle edilirse  
- Honeypot config dosyalarının saldırganca değiştirilmesi  
- DIM log’larının integrity kontrolünün olmaması  

## Risk Seviyesi  
**Medium**

## Mitigasyon
- DIM event loglarında HMAC doğrulaması  
- Config dosyaları sadece backend tarafından imzalı olmalı  
- Environment variable ORTAMI dışarı kapalı olmalı

---

# 🌐 9. A09 – Security Logging & Monitoring Failures

## Risk Açıklaması
Gözlem eksikliği → saldırılar fark edilmez.

## Projede Nasıl Ortaya Çıkabilir?
- Firewall → log üretmezse DIM öğrenemez  
- Behavior Engine → suspicious actions kaydedmez  
- Honeypot → tuzağa düşen saldırganları raporlamaz  
- Flask → 4xx/5xx loglanmaz

## Risk Seviyesi  
**High**

## Mitigasyon
- DIM → tüm eventleri normalized log formatında saklar  
- Log integrity (HMAC-SHA256)  
- Attack correlation  
- Dashboard (opsiyonel)

---

# 🌐 10. A10 – Server-Side Request Forgery (SSRF)

## Risk Açıklaması
Saldırgan backend’i proxy gibi kullanarak dış sistemlere istek gönderebilir.

## Projede Nasıl Ortaya Çıkabilir?
- Honeypot test endpoint’leri dış URL’lere erişiyorsa  
- Backend API dış adreslere güvenmeden call yapıyorsa  
- URL üzerinden file fetch işlemi varsa

## Risk Seviyesi  
**Medium**

## Mitigasyon
- URL allowlist  
- Internal network erişimi yasak  
- Validation Firewall → dış URL pattern’lerini engellesin  
- Request timeout + rate limit

---

# 🧩 Sonuç: Risk Özeti

| OWASP Maddesi | Risk Seviyesi | Etkilenen Modüller |
|---------------|----------------|--------------------|
| A01 | High | Firewall, Honeypot, BE |
| A02 | Medium | Session, DIM |
| A03 | Critical | Firewall, DIM, BE |
| A04 | High | Tüm mimari |
| A05 | Medium | Backend |
| A06 | Medium | Backend, Honeypot |
| A07 | High | Session, Firewall |
| A08 | Medium | DIM, Config |
| A09 | High | DIM, BE |
| A10 | Medium | Backend |

---

# 📌 Bu doküman Hafta 1 için referans alınacak olup, raporda “OWASP Risk Analizi hazırlanmıştır” şeklinde atıf yapılacaktır.
