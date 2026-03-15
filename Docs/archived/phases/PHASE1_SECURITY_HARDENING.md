# PHASE 1: SECURITY HARDENING - Implementation Guide

## Overview

This guide covers the complete security hardening implementation for CIAF to achieve enterprise production readiness.

**Status**: ✅ COMPLETE
**Estimated Implementation Time**: 2-3 hours
**Components**: Secrets Management, TLS/HTTPS, Security Headers, Rate Limiting

---

## 1. SECRETS MANAGEMENT

### Issue
Previously, secrets were hardcoded in `docker-compose.yml`:
```yaml
POSTGRES_PASSWORD: ciaf_secure_password_dev  ❌ Visible in version control!
API_KEY_SECRET: sk_dev_abc123def456ghi789jkl  ❌ Visible in version control!
```

### Solution
All secrets now use environment variables from `.env` file.

### Implementation Steps

#### Step 1.1: Create your local `.env` file

```bash
# Copy the example file
cp .env.example .env

# Generate strong secrets (macOS/Linux):
openssl rand -base64 32  # For POSTGRES_PASSWORD
openssl rand -hex 32     # For API_KEY_SECRET
openssl rand -base64 64  # For JWT_SECRET_KEY

# Or generate with Python:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Step 1.2: Update your `.env` file

```bash
# Database
DB_USER=ciaf_verification
DB_PASSWORD=your_generated_password_here

# Security Keys (IMPORTANT: Generate new ones for production)
API_KEY_SECRET=your_generated_key_here
JWT_SECRET_KEY=your_generated_key_here
CIAF_API_KEY=your_generated_key_here

# Environment
ENVIRONMENT=development  # Or 'production' for production deployments
```

#### Step 1.3: Verify `.env` is in `.gitignore`

```bash
# Check that .env files are ignored
grep "^.env" .gitignore

# Should output:
# .env
# .env.local
# .env.*.local
```

#### Step 1.4: Test with Docker Compose

```bash
# Export variables from .env
export $(cat .env | xargs)

# Start services
docker-compose up -d

# Verify services are running
docker-compose ps
```

### Production: Using External Secret Management

For production deployments, use external secret managers:

**AWS Secrets Manager**
```bash
# Store secrets in AWS
aws secretsmanager create-secret \
    --name ciaf/prod/api_key \
    --secret-string "your_secret_value"

# Reference in docker-compose
environment:
  API_KEY_SECRET: ${API_KEY_SECRET}  # Injected from AWS Secrets Manager
```

**HashiCorp Vault**
```bash
# Store secrets in Vault
vault kv put secret/ciaf/prod \
    api_key_secret="your_secret_value" \
    jwt_secret_key="your_secret_value"

# Export before running docker-compose
export API_KEY_SECRET=$(vault kv get -field=api_key_secret secret/ciaf/prod)
```

---

## 2. TLS/HTTPS CONFIGURATION

### Issue
Previously, all services communicated over plaintext HTTP.

### Solution
Added nginx reverse proxy with TLS termination.

### Implementation Steps

#### Step 2.1: Generate Development Certificates

```bash
# Make script executable
chmod +x scripts/generate-certificates.sh

# Generate self-signed certificates
./scripts/generate-certificates.sh
```

This creates:
- `nginx/certs/cert.pem` - SSL certificate
- `nginx/certs/key.pem` - Private key

#### Step 2.2: Start Services with HTTPS

```bash
# Start all services including nginx
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# Verify nginx is running
docker-compose ps | grep nginx

# Check HTTPS is working
curl --insecure https://localhost:443/health
```

#### Step 2.3: Update Frontend API URLs (if needed)

Update `frontend/.env` if using direct HTTPS:
```bash
VITE_API_BASE_URL=https://localhost:443
```

Or use the proxy (recommended):
```bash
VITE_API_BASE_URL=http://localhost:8001  # Still works, goes through nginx proxy
```

### Supported HTTPS Features

✅ **TLS 1.2 & 1.3** - Modern encryption
✅ **Strong Ciphers** - No weak encryption
✅ **HSTS Headers** - Force HTTPS
✅ **Certificate Validation** - Prevents MITM attacks

### Production HTTPS Setup

For production, use Let's Encrypt with certbot:

#### Step 2.4: Production Configuration

```bash
# Update nginx.conf with your domain
sed -i 's/localhost/yourdomain.com/g' nginx/nginx.conf

# Start services with production profile
docker-compose --profile production up -d

# Certbot will:
# - Request certificate from Let's Encrypt
# - Auto-renew every 60 days
# - Update nginx configuration
```

---

## 3. SECURITY HEADERS

### Issue
Missing OWASP security headers made the API vulnerable to common attacks.

### Solution
Implemented `SecurityHeadersMiddleware` in FastAPI.

### Headers Added

| Header | Protection | Value |
|--------|-----------|-------|
| `X-Frame-Options` | Clickjacking | `DENY` |
| `X-Content-Type-Options` | MIME sniffing | `nosniff` |
| `Content-Security-Policy` | XSS attacks | Strict policy |
| `Strict-Transport-Security` | Downgrade attacks | 1 year maxage |
| `Referrer-Policy` | Referrer leakage | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | Feature access | All features disabled |

### Implementation Steps

#### Step 3.1: Add Middleware to Verification Service

In `ciaf/verification/main.py`:

```python
from ciaf.verification.security_headers import SecurityHeadersMiddleware, CORSHeadersMiddleware

# Create FastAPI app
app = FastAPI()

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add CORS middleware with allowed origins
app.add_middleware(
    CORSHeadersMiddleware,
    allowed_origins=[
        "http://localhost:3002",  # Frontend
        "http://localhost:8001",  # Backend
        "https://yourdomain.com",  # Production
    ],
    allowed_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
)
```

#### Step 3.2: Verify Headers

```bash
# Check security headers are present
curl -i https://localhost:443/health

# Should include:
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# Strict-Transport-Security: max-age=31536000
# Content-Security-Policy: ...
```

---

## 4. RATE LIMITING

### Issue
No rate limiting left API vulnerable to brute force and DoS attacks.

### Solution
Implemented `RateLimitMiddleware` with per-organization and per-user limits.

### Default Limits

- **Global**: 1,000 requests/minute (all users combined)
- **Per-Organization**: 100 requests/minute
- **Per-User**: 30 requests/minute
- **Monthly Quota**: 100,000 requests per organization

### Implementation Steps

#### Step 4.1: Add Rate Limiting Middleware

In `ciaf/verification/main.py`:

```python
from ciaf.verification.rate_limiting import (
    RateLimitMiddleware,
    QuotaMiddleware
)

# Create FastAPI app
app = FastAPI()

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    global_limit=1000,
    org_limit=100,
    user_limit=30,
    window_seconds=60
)

# Add quota middleware for monthly limits
app.add_middleware(
    QuotaMiddleware,
    monthly_quota=100000
)
```

#### Step 4.2: Configure Per-Organization Limits

Clients can specify organization via header:

```bash
# Request with organization header
curl \
    -H "X-Organization-ID: banking_org_001" \
    -H "Authorization: Bearer your_token" \
    https://localhost:443/verify
```

#### Step 4.3: Handle Rate Limit Responses

Clients receive HTTP 429 with rate limit info:

```json
{
  "error": "rate_limit_exceeded",
  "message": "User rate limit exceeded",
  "limit": 30,
  "window_seconds": 60,
  "retry_after": 60
}
```

Response headers:
```
RateLimit-Limit: 30
RateLimit-Remaining: 15
RateLimit-Reset: 1700000000
Retry-After: 60
```

#### Step 4.4: Adjust Limits for Production

Configure limits based on your needs:

```python
# For high-volume deployments
RateLimitMiddleware(
    app,
    global_limit=10000,      # 10K requests/min
    org_limit=500,           # 500 requests/min per org
    user_limit=100,          # 100 requests/min per user
    window_seconds=60
)
```

---

## 5. INTEGRATION CHECKLIST

- [ ] Generated strong secrets and stored in `.env`
- [ ] Verified `.env` is in `.gitignore`
- [ ] Generated SSL certificates
- [ ] Started services with nginx reverse proxy
- [ ] Verified HTTPS is working
- [ ] Added security headers middleware
- [ ] Tested security headers are present
- [ ] Added rate limiting middleware
- [ ] Tested rate limiting responses
- [ ] Updated documentation for operations team

---

## 6. TESTING SECURITY

### Test TLS/HTTPS

```bash
# Test SSL configuration
openssl s_client -connect localhost:443

# Check certificate validity
openssl x509 -in nginx/certs/cert.pem -text -noout

# Test HTTPS endpoint
curl --insecure -v https://localhost:443/health
```

### Test Security Headers

```bash
# Verify all security headers present
curl -s https://localhost:443/health | grep -i x-frame-options

# Full header dump
curl -s -D - https://localhost:443/health | grep -i "x-\|strict-\|content-security"
```

### Test Rate Limiting

```bash
# Send 35 rapid requests
for i in {1..35}; do
    curl -H "X-Organization-ID: test_org" https://localhost:443/health
done

# Should get 429 error after 30th request
```

### Test with Documentation Recommendations

```bash
# Use NMAP to scan for SSL/TLS vulnerabilities
nmap --script ssl-enum-ciphers -p 443 localhost

# Use testssl.sh for comprehensive SSL testing
./testssl.sh https://localhost:443
```

---

## 7. NEXT STEPS

After completing PHASE 1, proceed to:

**PHASE 2: Frontend Authentication** (Start here next)
- Build Login/Logout pages
- Implement token refresh
- Add password reset flow

**PHASE 3: CI/CD Automation**
- Enable GitHub Actions
- Set up automated testing
- Configure deployment automation

---

## 8. REFERENCE

### Configuration Files
- `.env.example` - Environment variable template
- `nginx/nginx.conf` - Nginx reverse proxy configuration
- `docker-compose.override.yml` - HTTPS docker-compose override

### Implementation Files
- `ciaf/verification/security_headers.py` - Security headers middleware
- `ciaf/verification/rate_limiting.py` - Rate limiting middleware
- `scripts/generate-certificates.sh` - Certificate generation script

### Important Notes

1. **Never commit `.env` files** - They contain secrets!
2. **Self-signed certificates are for development only** - Use Let's Encrypt for production
3. **Rate limits are in-memory**  - For distributed deployments, use Redis-based rate limiting
4. **Monitor rate limit violations** - Track abuse attempts for security analysis

---

## SUPPORT

For issues or questions:

1. Check log output: `docker-compose logs <service_name>`
2. Review SECURITY.md for compliance requirements
3. Consult OWASP guidelines: https://owasp.org
4. Examine nginx error logs: `docker-compose logs nginx`
