SECURITY TEST SCENARIOS 

Document Owner: Beyza Beril Yalçınkaya
Scope: Security Validation & Access Control Verification

This document defines the standard test procedures to be applied for validating the system's security layers.

1. SQL Injection (SQLi) Test Procedure

Target: Login Panel and Search Functions

Test ID: SQL-LOGIN-01

Scenario: Authentication bypass attempt.

Input: Entering the payload ' OR '1'='1 into the username field.

Expected Result: System must deny access and return a generic error message ("Invalid credentials").

Test ID: SQL-UNION-02

Scenario: Data Exfiltration attempt.

Input: Injection of UNION SELECT table_name FROM information_schema.tables into the URL parameter.

Expected Result: Database structure must not be disclosed; server should return 400 Bad Request or sanitized output.

2. Cross-Site Scripting (XSS) Test Procedure

Target: Profile Update and Comment Fields

Test ID: XSS-REFLECTED-01

Scenario: URL-based script execution.

Input: http://site.com/search?q=<script>alert(1)</script>

Expected Result: Browser must not open an alert window; special characters must be encoded as HTML entities (&lt;script&gt;).

Test ID: XSS-STORED-02

Scenario: Persistent malicious content storage.

Input: Saving <img src=x onerror=alert('Hacked')> code into the Profile biography.

Expected Result: Tags must be cleaned during database save as per sanitization_profiles.json rules.

3. Access Control Test Procedure

Target: Admin Panel (/admin)

Test ID: AC-ROLE-01

Scenario: Unauthorized user access (Vertical Privilege Escalation).

Steps: Log in with a standard user (Role: User) and attempt to send a direct request to /admin/dashboard.

Expected Result: Server must return a 403 Forbidden response.

Test ID: AC-SESSION-02

Scenario: Sessionless access.

Steps: Log out of the system and attempt to access a protected page.

Expected Result: User must be automatically redirected to the login page (302 Redirect -> /login).