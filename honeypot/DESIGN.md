# Honeypot Design Document

## 1. Overview
Bu modül, web uygulamasına yönelik saldırıları tespit etmek ve saldırganı oyalamak için tasarlanmıştır.

## 2. Honeypot Types
- **Fake Admin Panel:** `/admin-panel` adresinde bulunur. Brute-force saldırılarını loglar.
- **Fake DB Endpoint:** `/api/v1/user-data` adresinde bulunur. SQL Injection denemelerinde sahte hata mesajları döner.

## 3. Simulation Plans
- Brute Force
- SQL Injection (SQLi)
- XSS (Cross-Site Scripting)