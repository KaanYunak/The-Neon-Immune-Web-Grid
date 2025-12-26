# Bu dosya, farklı tuzak tiplerini ve onların risk ağırlıklarını tanımlar.
# Hafta 4: Honeypot çeşitliliği görevi.

HONEYPOT_TEMPLATES = {
    "SENSITIVE_FILE": {
        "path": "/.env",
        "type": "FILE_INCLUSION",
        "risk_weight": 5, # Çok kritik dosya, direkt bloklama sebebi
        "response_type": "text",
        "fake_content": "DB_HOST=127.0.0.1\nDB_PASS=s3cr3t_k3y_do_not_share"
    },
    "BACKUP_DB": {
        "path": "/backup.sql",
        "type": "DATA_LEAK",
        "risk_weight": 3,
        "response_type": "text",
        "fake_content": "-- MySQL dump 10.13\n-- Server version 5.7.32\nINSERT INTO `users` VALUES (1,'admin','hash_x92');"
    },
    "IOT_SHELL": {
        "path": "/shell",
        "type": "RCE_ATTEMPT",
        "risk_weight": 4,
        "response_type": "json",
        "fake_content": {"error": "command not found", "status": 127}
    },
    "OLD_ADMIN": {
        "path": "/administrator",
        "type": "LEGACY_PROBE",
        "risk_weight": 2,
        "response_type": "html",
        "fake_content": "fake_admin.html" # Şablona yönlendirir
    }
}