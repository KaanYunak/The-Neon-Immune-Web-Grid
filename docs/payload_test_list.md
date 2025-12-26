Security Testing Payloads (Week 2)

Author: Beyza Beril Yalçınkaya
Module: Security Validation & Threat Modeling

Bu liste, geliştirdiğimiz "Validation Firewall" ve "Sanitization" modüllerini test etmek için kullanılacaktır.

1. SQL Injection (SQLi)

Amaç: Veritabanı sorgularını manipüle etmek.

' OR '1'='1 (Login Bypass)

' UNION SELECT 1, username, password FROM users-- (Veri Sızdırma)

admin' -- (Yorum satırı testi)

1; DROP TABLE users (Yıkıcı komut)

2. Cross-Site Scripting (XSS)

Amaç: İzinsiz script çalıştırmak.

<script>alert('Hacked')</script>

<img src=x onerror=alert(1)>

<svg/onload=alert('XSS')>

javascript:alert(1)

3. Command Injection (RCE)

Amaç: Sunucu terminalinde komut çalıştırmak.

; ls -la

| cat /etc/passwd

& ping 8.8.8.8

4. Logic Flaws

Amaç: İş mantığını bozmak.

id=-1

price=0

quantity=9999999999