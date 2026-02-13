# Security Hardening Checklist

## Completed Hardening Measures

### 1. Rate Limiting ✅
- **Login endpoint**: 5 attempts per 15 minutes
- **Register endpoint**: 3 attempts per 1 hour
- **Default**: 200 per day, 50 per hour globally
- **Library**: Flask-Limiter
- **Config**: `RATE_LIMIT_DEFAULT`, `RATE_LIMIT_STORAGE` env vars

### 2. File Upload Validation ✅
- **Size limit**: 10 MB per file
- **Allowed types**: PNG, JPG, JPEG, PDF
- **MIME type checking**: Only safe MIME types (image/*, application/pdf)
- **Filename sanitization**: secure_filename() + UUID prefix
- **Endpoints protected**:
  - `/activities/new` (proof files)
  - `/activities/<id>/edit` (proof files)
  - `/profile` (profile images)
- **Storage**: Firebase Cloud Storage (private, accessed via signed URLs)

### 3. Secure Headers ✅
- `X-Content-Type-Options: nosniff` — prevents MIME sniffing
- `X-Frame-Options: DENY` — prevents clickjacking
- `X-XSS-Protection: 1; mode=block` — legacy XSS protection
- `Strict-Transport-Security` — enforces HTTPS (when SECURE cookies enabled)
- `Referrer-Policy: strict-origin-when-cross-origin` — limits referrer leakage
- `Permissions-Policy` — restricts browser features (geolocation, camera, etc.)

### 4. CSRF Protection ✅
- Flask-WTF CSRFProtect enabled globally
- Tokens on all state-changing forms (POST/PUT/DELETE)
- Session-based CSRF tokens

### 5. Session & Cookie Hardening ✅
- `SESSION_COOKIE_SECURE=True` — HTTPS only (configurable via env)
- `SESSION_COOKIE_HTTPONLY=True` — prevents JS access
- `SESSION_COOKIE_SAMESITE=Lax` — prevents CSRF via cookies
- Session lifetime: 1 hour (configurable via `SESSION_LIFETIME_HOURS`)
- Config-driven (no hardcoded defaults)

### 6. Secret Key Management ✅
- Required in production (fails fast if missing)
- Development fallback only when `FLASK_ENV=development`
- Min 32 characters recommended (enforce via docs)

### 7. File Input Validation ✅
- Extension whitelist (only png, jpg, jpeg, pdf)
- MIME type validation
- File size validation (10 MB)
- Empty file rejection
- Content-Type header fallback check

---

## Recommended Additional Measures (Future)

### High Priority
- [ ] **Virus/Malware Scanning**: Integrate ClamAV or VirusTotal API for uploaded files
- [ ] **SQL Injection Prevention**: Already mitigated by Firestore (no SQL), but ensure input sanitization in future custom queries
- [ ] **Token Expiry & Refresh**: Add refresh token flow for Firebase ID tokens (currently relies on session expiry)
- [ ] **Account Lockout**: Lock account after N failed login attempts for X minutes
- [ ] **2FA/MFA**: Add TOTP or SMS-based second factor for admin/sensitive operations
- [ ] **Input Sanitization**: Sanitize user input on backend to prevent XSS (esp. activity titles, descriptions)
- [ ] **API Rate Limiting per User**: Different limits for authenticated vs. anonymous users
- [ ] **Password Policy Enforcement**: Min length, complexity, no reuse (in Firebase auth)

### Medium Priority
- [ ] **Audit Logging**: Log all admin actions (approvals, rejections) for compliance
- [ ] **Data Encryption at Rest**: Firestore rules + GCP encryption settings review
- [ ] **Secrets Rotation**: Automated rotation of API keys (SendGrid, n8n, etc.)
- [ ] **Dependency Scanning**: `pip-audit` in CI/CD (see CI setup)
- [ ] **SAST**: Static security analysis (Bandit, Semgrep)
- [ ] **DAST**: Dynamic testing (OWASP ZAP, Burp)

### Lower Priority (Nice to Have)
- [ ] **Content Security Policy (CSP)**: Restrict script/style/font sources
- [ ] **WAF (Web Application Firewall)**: Deploy behind Cloudflare WAF or AWS WAF
- [ ] **DDoS Protection**: Rate limiting at CDN/WAF level
- [ ] **IP Whitelisting**: For admin panel (if internal-only)
- [ ] **VPN/SSH Tunneling**: For secure access to staging/production

---

## Environment Variables for Security

See `.env.example` for:
- `FLASK_SECRET_KEY` — required
- `SESSION_COOKIE_SECURE` — set to True in prod
- `SESSION_COOKIE_SAMESITE` — Lax or Strict
- `SESSION_LIFETIME_HOURS` — session duration
- `RATE_LIMIT_DEFAULT` — global rate limit
- `RATE_LIMIT_STORAGE` — memory://, redis://, etc.

---

## Testing Security Measures

### Rate Limiting
```bash
# Test login rate limiting (5 per 15 min)
for i in {1..10}; do curl -X GET http://localhost:5000/login; done
# After 5 attempts, should see 429 Too Many Requests
```

### File Upload Validation
```bash
# Test with oversized file (>10 MB)
dd if=/dev/zero of=test_large.bin bs=1M count=11
curl -F "proof_file=@test_large.bin" http://localhost:5000/activities/new

# Test with invalid MIME type
echo "malicious content" > fake.pdf
curl -F "proof_file=@fake.pdf" http://localhost:5000/activities/new
```

### Secure Headers
```bash
curl -I http://localhost:5000
# Should see X-Content-Type-Options, X-Frame-Options, etc.
```

### CSRF Protection
```bash
# Test POST without CSRF token — should fail
curl -X POST http://localhost:5000/activities/new \
  -d "title=test&provider=test"
# Should get 400 Bad Request (CSRF token missing)
```

---

## Security Best Practices Checklist

- [ ] Review Firestore security rules (no overly permissive rules)
- [ ] Enable audit logging in Firebase Console
- [ ] Use a VPN or private network for production deployment
- [ ] Rotate service account keys regularly (GCP)
- [ ] Whitelist IP ranges for critical APIs (if applicable)
- [ ] Document incident response plan
- [ ] Schedule quarterly security reviews / pen-tests
- [ ] Keep dependencies updated (`pip-audit` in CI)
- [ ] Monitor logs for anomalies (Sentry, CloudWatch, etc.)
- [ ] Have a data backup & recovery plan

---

## Next Steps

1. **Deploy with hardening enabled** (all measures above are active)
2. **Test rate limiting and file upload validation** in staging
3. **Add virus scanning** for uploaded files (optional but recommended)
4. **Set up monitoring/alerting** for security events (see Observability)
5. **Schedule penetration test** before production release
6. **Document security architecture** in a Security.md or similar

---

*Last updated: February 6, 2026*
