Incident Response Workflow

Bu diyagram, sistemde bir saldırı tespit edildiğinde izlenecek otomatik ve manuel adımları gösterir.

graph TD
    A["Saldırı Tespiti (Detection)"] -->|"WAF ve Behavior Engine"| B{"Tehdit Skoru > 70?"}
    B -- Hayır --> C["Logla ve İzlemeye Devam Et"]
    B -- Evet --> D["Otomatik Engelleme (Containment)"]
    
    D --> E["IP Adresini Blocklist'e Ekle"]
    D --> F["Oturumu (Session) Sonlandır"]
    D --> G["Honeypot'a Yönlendir (Opsiyonel)"]
    
    E --> H["Olay Analizi (Analysis)"]
    F --> H
    
    H --> I{"Saldırı Tipi Nedir?"}
    I -- "SQLi / XSS" --> J["Sanitization Kurallarını Güncelle"]
    I -- "Brute Force" --> K["Rate Limit Ayarlarını Sıkılaştır"]
    
    J --> L["Sistemi Normale Döndür (Recovery)"]
    K --> L
    L --> M["Raporlama (Post-Incident)"]
