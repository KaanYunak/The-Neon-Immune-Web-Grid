
# Session Security Design – The Neon Immune Web Grid

## 1. Session Storage Strategy
- Server-side signed cookies (Flask default session)
- SECRET_KEY minimum 32-byte strong random key
- Session data MUST NOT contain:
  - passwords
  - tokens
  - user roles in plaintext
  - raw input data
- Optional: Redis session store for hardened mode (future sprint)

---

## 2. Cookie Security Flags
| Flag | Value | Purpose |
|------|--------|----------|
| HttpOnly | True | JS üzerinden çalınmayı engeller |
| Secure | True | HTTPS olmayan ortamda cookie gönderilmez |
| SameSite | Strict | CSRF riskini düşürür |
| Path | "/" | Tüm uygulama için geçerli |

---

## 3. Session Lifetime
- Idle timeout: **15 minutes**
- Absolute timeout: **6 hours**
- Logout → session token invalidation

---

## 4. Authentication Token Policy
- SessionID + rotating anti-CSRF token
- Token rotation:
  - Login
  - Privilege change
  - Suspicious behavior detection (DIM + Firewall)

---

## 5. Suspicious Session Behaviors (Triggers)
- Too many failed logins
- Rapid request bursts
- Accessing restricted endpoints without proper role
- Honeypot endpoint detection
- XSS/SQLi signature inside request

These events will trigger:
- Session invalidation OR
- Session downgrade (read-only mode) OR
- IP temporary ban (Firewall module)

---

## 6. Secure Logout Flow
1. Invalidate session token
2. Clear cookie
3. Regenerate CSRF token
4. Log event into **Digital Immune Memory**

---

## 7. Integration Points
- Validation Firewall (input validation)
- Digital Immune Memory (DIM)
- Honeypot Redirection Engine
