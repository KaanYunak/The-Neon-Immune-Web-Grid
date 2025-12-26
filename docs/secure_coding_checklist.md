Project: The Neon Immune Web Grid
Maintainers: Beyza Beril Yalçınkaya (Security Validation), Kaan Yunak (Lead Security)
Last Updated: Week 2 (Sprint 2)

Bu belge, The Neon Immune Web Grid projesinin geliştirme sürecinde uyulması gereken güvenlik standartlarını ve doğrulama adımlarını tanımlar. Kod inceleme süreçlerinde ve entegrasyon aşamalarında bu listedeki maddelerin doğrulanması zorunludur.

Input Validation & Sanitization (Girdi Doğrulama ve Temizleme)

Tüm kullanıcı girdilerinin validation_firewall.py modülü üzerinden geçtiği doğrulanmalıdır.
Kod içine gömülü (hard-coded) kurallar yerine security/sanitization_profiles.json dosyasındaki merkezi kuralların kullanıldığı kontrol edilmelidir.
Her veri girişi için tip kontrolü (integer, string, email) sunucu tarafında zorunlu tutulmalıdır.
Girdiler için minimum ve maksimum karakter uzunlukları belirlenerek Buffer Overflow riskleri elimine edilmelidir.
Yasaklı karakterleri engellemek yerine, sadece izin verilen karakter setlerini kabul eden Whitelist yaklaşımı benimsenmelidir.
Kullanıcı girdilerinin eval(), exec() veya os.system() gibi kritik fonksiyonlara doğrudan parametre olarak verilmediği teyit edilmelidir.

Authentication & Session Management (Kimlik ve Oturum Yönetimi)

Kullanıcı şifrelerinin veritabanında asla düz metin olarak saklanmadığı, Argon2 veya Bcrypt gibi güçlü algoritmalarla hash'lendiği doğrulanmalıdır.
Oturum çerezlerinde (cookies) HttpOnly, Secure ve SameSite=Strict bayraklarının aktif olduğu kontrol edilmelidir.
Başarılı giriş işlemlerinden sonra oturum sabitleme (Session Fixation) saldırılarını önlemek amacıyla oturum anahtarının yenilendiği teyit edilmelidir.
Giriş ve kayıt ekranlarında kaba kuvvet (Brute-Force) saldırılarına karşı IP tabanlı hız sınırlama (Rate Limiting) mekanizmasının çalıştığı doğrulanmalıdır.

Output Encoding & XSS Prevention (Çıktı Güvenliği)

HTML içeriğinde dinamik olarak gösterilen tüm kullanıcı verilerinin, bağlama uygun şekilde (Context-Aware Encoding) kodlandığı kontrol edilmelidir.
Otomatik kaçış (autoescape) mekanizmalarının devre dışı bırakılmadığı ve safe filtresinin kullanımının sınırlandırıldığı doğrulanmalıdır.
Tarayıcı tarafında XSS saldırılarını azaltmak için Content-Security-Policy (CSP) başlığının HTTP yanıtlarına eklendiği teyit edilmelidir.

Access Control (Erişim Denetimi)

Varsayılan olarak tüm uç noktaların (endpoints) erişime kapalı olduğu (Deny by Default) ilkesinin uygulandığı kontrol edilmelidir.
Yönetici paneli ve hassas verilere erişim sağlayan fonksiyonlarda rol tabanlı erişim kontrolü (RBAC) dekoratörlerinin eksiksiz kullanıldığı doğrulanmalıdır.
Kullanıcıların sadece kendi yetki alanlarındaki verilere erişebildiği, IDOR (Insecure Direct Object Reference) zafiyetlerine karşı test edilmelidir.

Logging & Error Handling (Loglama ve Hata Yönetimi)

Log kayıtlarında şifre, kredi kartı bilgisi veya kimlik doğrulama tokenları gibi hassas verilerin yer almadığı kontrol edilmelidir.
Kritik güvenlik olaylarının bütünlüğünü korumak amacıyla logging_secure.py modülü üzerinden zincirleme hash (Hash-Chaining) yöntemiyle kaydedildiği doğrulanmalıdır.
Kullanıcılara gösterilen hata mesajlarının sistem iç yapısına dair detay (stack trace, SQL sorgusu vb.) barındırmadığı teyit edilmelidir.

Honeypot Integration (Tuzak Sistem Entegrasyonu)

Honeypot veritabanı ile gerçek üretim veritabanının fiziksel ve mantıksal olarak tam izolasyonu sağlanmalıdır.
Tuzak sisteme yönlendirilen şüpheli trafiğin gerçek sisteme geri dönüş yolunun kapatıldığı doğrulanmalıdır.
Sahte yönetici paneline yapılan erişim girişimlerinin Davranış Analiz Motoruna (Behavior Engine) yüksek öncelikli tehdit olarak raporlandığı kontrol edilmelidir.