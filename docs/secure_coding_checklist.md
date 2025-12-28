
Project: The Neon Immune Web Grid  
Maintainers: Beyza Beril Yalçınkaya (Security Validation), Kaan Yunak (Lead Security)  
Last Updated: Week 5 (Sprint 5)  
Version: Final

Bu belge, The Neon Immune Web Grid projesinin geliştirme sürecinde uyulması gereken güvenlik standartlarını ve doğrulama adımlarını tanımlar. Kod inceleme süreçlerinde ve entegrasyon aşamalarında bu listedeki maddelerin doğrulanması zorunludur.

---

### Input Validation & Sanitization (Girdi Doğrulama ve Temizleme)
- [ ] Tüm kullanıcı girdileri validation_firewall.py modülünden geçiyor.  
	_Doğrulama: Kod incelemesi, otomasyon_
- [ ] Merkezi kurallar security/sanitization_profiles.json üzerinden uygulanıyor.  
	_Doğrulama: Kod incelemesi_
- [ ] Tip kontrolü (integer, string, email) zorunlu.  
	_Doğrulama: Kod incelemesi_
- [ ] Karakter uzunlukları sınırlandırılmış.  
	_Doğrulama: Kod incelemesi_
- [ ] Whitelist karakter seti kullanılıyor.  
	_Doğrulama: Kod incelemesi_
- [ ] eval(), exec(), os.system() gibi fonksiyonlara doğrudan kullanıcı girdisi verilmiyor.  
	_Doğrulama: Kod incelemesi_

### Authentication & Session Management (Kimlik ve Oturum Yönetimi)
- [ ] Şifreler Argon2/Bcrypt ile hash’leniyor, düz metin yok.  
	_Doğrulama: Kod incelemesi, otomasyon_
- [ ] Oturum çerezlerinde HttpOnly, Secure, SameSite=Strict aktif.  
	_Doğrulama: Kod incelemesi, manuel test_
- [ ] Oturum anahtarı başarılı girişte yenileniyor.  
	_Doğrulama: Kod incelemesi_
- [ ] Brute-force saldırılarına karşı rate limiting aktif.  
	_Doğrulama: Otomasyon, manuel test_

### Output Encoding & XSS Prevention (Çıktı Güvenliği)
- [ ] Tüm kullanıcı verileri context-aware encoding ile kodlanıyor.  
	_Doğrulama: Kod incelemesi, otomasyon_
- [ ] Autoescape devre dışı değil, safe filtresi kısıtlı.  
	_Doğrulama: Kod incelemesi_
- [ ] Content-Security-Policy (CSP) başlığı ekli.  
	_Doğrulama: Manuel test, header kontrolü_

### Access Control (Erişim Denetimi)
- [ ] Varsayılan olarak tüm endpointler kapalı (Deny by Default).  
	_Doğrulama: Kod incelemesi_
- [ ] RBAC dekoratörleri yönetici panelinde eksiksiz.  
	_Doğrulama: Kod incelemesi_
- [ ] IDOR zafiyetlerine karşı test yapıldı.  
	_Doğrulama: Otomasyon, manuel test_

### Logging & Error Handling (Loglama ve Hata Yönetimi)
- [ ] Loglarda hassas veri yok.  
	_Doğrulama: Kod incelemesi_
- [ ] Loglar hash-chaining ile korunuyor.  
	_Doğrulama: Kod incelemesi, otomasyon_
- [ ] Hata mesajları sistem içeriği sızdırmıyor.  
	_Doğrulama: Manuel test_

### Honeypot Integration (Tuzak Sistem Entegrasyonu)
- [ ] Honeypot ve üretim veritabanı izole.  
	_Doğrulama: Kod incelemesi_
- [ ] Tuzak sisteme yönlendirilen trafik geri dönemiyor.  
	_Doğrulama: Kod incelemesi_
- [ ] Sahte admin paneli saldırıları Behavior Engine’e raporlanıyor.  
	_Doğrulama: Kod incelemesi, otomasyon_