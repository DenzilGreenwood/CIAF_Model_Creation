# Environment Setup Guide

Configure your development, staging, and production environments.

## Quick Setup (5 Minutes)

### Prerequisites

- Docker & Docker Compose (recommended)
- OR Python 3.9+ + Node 18+ (for native setup)
- Git

### Docker Setup (Fastest)

```bash
# Clone and navigate
git clone https://github.com/your-org/ciaf.git
cd ciaf

# Copy environment template
cp .env.example .env

# Start all services
docker-compose up -d

# Verify services
docker-compose logs -f verification-service
```

**Expected output:**
```
verification-service | ✅ Starting CIAF Verification Service on http://localhost:8000
verification-service | ✅ Database initialized
verification-service | ✅ Health check passed
```

Visit: **http://localhost:3000** (Dashboard)

### Native Setup (For Development)

**Backend:**
```bash
cd ciaf
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m ciaf.verification.api
```

Expected: `Uvicorn running on http://127.0.0.1:8000`

**Frontend:**
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

Expected: `Local: http://localhost:5173`

---

## Environment Variables

### Development (.env)

```bash
# Backend
DATABASE_URL=sqlite:///./ciaf_proofs.db
SQLALCHEMY_ECHO=1
LOG_LEVEL=DEBUG

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# Frontend (pointing to local backend)
VITE_API_BASE_URL=http://localhost:8000
VITE_VAULT_URL=http://localhost:9000
VITE_APP_ENV=development

# Vault (if running locally)
VAULT_DATABASE_URL=sqlite:///./ciaf_vault.db
VAULT_JWT_SECRET=dev-vault-secret

# Observability
PROMETHEUS_ENABLED=false  # Lightweight for dev
LOG_FORMAT=simple

# Optional: LLM for demos
OPENAI_API_KEY=sk-...
OLLAMA_URL=http://localhost:11434
```

### Staging (.env.staging)

```bash
# Backend - Connect to staging PostgreSQL
DATABASE_URL=postgresql://ciaf_user:${STAGING_DB_PASSWORD}@staging-db.internal:5432/ciaf_proofs
SQLALCHEMY_ECHO=0
LOG_LEVEL=INFO

# JWT - Use strong secrets, store in secret manager
JWT_SECRET_KEY=${STAGING_JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# Frontend - Point to staging backend
VITE_API_BASE_URL=https://api.staging.ciaf.io
VITE_VAULT_URL=https://vault.staging.ciaf.io
VITE_APP_ENV=staging

# Vault - PostgreSQL backend
VAULT_DATABASE_URL=postgresql://ciaf_vault:${STAGING_VAULT_PASSWORD}@staging-db.internal:5432/ciaf_vault
VAULT_JWT_SECRET=${STAGING_VAULT_SECRET}

# Observability
PROMETHEUS_ENABLED=true
GRAFANA_URL=https://monitoring.staging.ciaf.io
LOG_FORMAT=json.l

# TLS
TLS_ENABLED=true
TLS_CERTIFICATE=/etc/certs/staging.crt
TLS_KEY=/etc/certs/staging.key
```

### Production (.env.production)

```bash
# Backend - HA PostgreSQL with read replicas
DATABASE_URL=postgresql://ciaf_user:${PROD_DB_PASSWORD}@prod-db-primary.internal:5432/ciaf_proofs
DATABASE_REPLICA_URL=postgresql://ciaf_user:${PROD_DB_PASSWORD}@prod-db-replica.internal:5432/ciaf_proofs
POOL_SIZE=50
MAX_OVERFLOW=20
SQLALCHEMY_ECHO=0
LOG_LEVEL=WARN

# JWT - Rotate keys every 90 days
JWT_SECRET_KEY=${PROD_JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=8  # Shorter expiry in production

# Frontend - Production CDN
VITE_API_BASE_URL=https://api.ciaf.io
VITE_VAULT_URL=https://vault.ciaf.io
VITE_APP_ENV=production

# Vault - Separate HA PostgreSQL
VAULT_DATABASE_URL=postgresql://ciaf_vault:${PROD_VAULT_PASSWORD}@prod-vault-db.internal:5432/ciaf_vault
VAULT_REPLICA_URL=postgresql://ciaf_vault:${PROD_VAULT_PASSWORD}@prod-vault-db-replica.internal:5432/ciaf_vault
VAULT_JWT_SECRET=${PROD_VAULT_SECRET}

# Observability - Full monitoring stack
PROMETHEUS_ENABLED=true
PROMETHEUS_RETENTION_DAYS=30
GRAFANA_URL=https://monitoring.ciaf.io
LOG_FORMAT=json.l
LOG_DESTINATION=cloudwatch  # AWS CloudWatch for centralized logging

# TLS - Strict HTTPS
TLS_ENABLED=true
TLS_CERTIFICATE=/etc/secrets/prod.crt
TLS_KEY=/etc/secrets/prod.key
TLS_MIN_VERSION=1.2

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=100

# Backup & Disaster Recovery
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"  # Daily at 2 AM
BACKUP_DESTINATION=s3://backups-ciaf/ # AWS S3
```

---

## Configuration by Environment

### Development (Local)

| Component | URL | Purpose |
|-----------|-----|---------|
| Frontend | http://localhost:3000 | React app (Vite dev server) |
| Backend API | http://localhost:8000 | Verification service |
| Vault | http://localhost:9000 | Evidence custodian |
| PostgreSQL | localhost:5432 | (if using Docker) |
| Prometheus | http://localhost:9090 | Metrics (if enabled) |
| Grafana | http://localhost:3001 | Dashboards (if enabled) |

### Staging

| Component | URL | Purpose |
|-----------|-----|---------|
| Frontend | https://app.staging.ciaf.io | React app (CDN) |
| Backend API | https://api.staging.ciaf.io | Verification service (ELB) |
| Vault | https://vault.staging.ciaf.io | Evidence custodian (ELB) |
| RDS PostgreSQL | staging-db.internal:5432 | Multi-AZ |
| Prometheus | https://prometheus.staging.ciaf.io | Metrics collection |
| Grafana | https://monitoring.staging.ciaf.io | Dashboards & alerting |

### Production

| Component | URL | Purpose |
|-----------|-----|---------|
| Frontend | https://ciaf.io | React app (CloudFront CDN) |
| Backend API | https://api.ciaf.io | Verification service (ALB, multi-AZ) |
| Vault | https://vault.ciaf.io | Evidence custodian (ALB, multi-AZ) |
| RDS PostgreSQL | prod-db.internal:5432 | Multi-AZ with read replicas |
| Vault DB | prod-vault-db.internal:5432 | Separate HA cluster for custody |
| Prometheus | https://prometheus.ciaf.io | Metrics aggregation |
| Grafana | https://monitoring.ciaf.io | Global dashboards & alerting |
| Jaeger | https://trace.ciaf.io | Distributed tracing |

---

## Database Setup

### Development (SQLite)

```bash
# No setup needed! SQLite is file-based
# Database auto-creates at ~/.ciaf/proof_store.db
ls -la ~/.ciaf/proof_store.db
```

### Production (PostgreSQL)

**First-time setup:**

```bash
# Create database and user
psql -U postgres -c "CREATE USER ciaf_user WITH PASSWORD 'secure_password';"
psql -U postgres -c "CREATE DATABASE ciaf_proofs OWNER ciaf_user;"

# Run Alembic migrations
cd ciaf
alembic upgrade head

# Verify tables
psql -U ciaf_user -d ciaf_proofs -c "\dt"
```

**Schema includes:**
- ✅ output_tags (proof records)
- ✅ task_batches (Merkle batches)
- ✅ agent_actions (audit trail)
- ✅ verification_events (read logs)
- ✅ organizations (multi-tenant)

Full details: [PostgreSQL Migration Guide](../00-docs/POSTGRESQL_MIGRATION_GUIDE.md)

---

## Multi-Tenancy Configuration

Each organization instance is isolated at the database level:

```python
# ciaf/core/config.py
ORGANIZATION_ID = os.getenv("ORGANIZATION_ID", "default-org")

# All queries automatically filtered:
# SELECT * FROM output_tags
# WHERE organization_id = ORGANIZATION_ID
```

**To run separate org instances:**

```bash
# Healthcare Org
ORGANIZATION_ID=healthcare-org-1 python -m ciaf.verification.api --port 8001

# Banking Org
ORGANIZATION_ID=banking-org-1 python -m ciaf.verification.api --port 8002
```

Each org has:
- Separate API endpoint
- Separate database schema
- Separate Vault instance (recommended)
- Independent audit trails

---

## Troubleshooting

### Backend Won't Start

```
Error: Address already in use [:8000]
```

**Fix:** Another process on port 8000?
```bash
lsof -i :8000          # Find process
kill -9 <PID>          # Kill it
python -m ciaf.verification.api  # Restart
```

### Database Connection Error

```
psycopg2.OperationalError: could not connect to server: ...
```

**Fix:** Check DATABASE_URL
```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/ciaf_proofs"
# OR use .env file
cat .env | grep DATABASE_URL
```

### Frontend Can't Reach Backend

```
CORS error: Cross-Origin Request Blocked
```

**Fix:** Frontend env pointing to wrong backend?
```bash
# .env file in frontend/
VITE_API_BASE_URL=http://localhost:8000

# Restart
npm run dev
```

### Vault API Key Not Working

```
401 Unauthorized: Invalid API Key
```

**Fix:** Export VAULT_API_KEY?
```bash
export VAULT_API_KEY=your_key_here
# OR pass as header:
curl -H "X-API-Key: your_key_here" http://localhost:9000/...
```

---

## Next Steps

- [5-Minute Flow](./5min-compliance-flow.md) - Get up and running
- [API Authentication](./api-auth.md) - Learn to authenticate requests
- [LCM Deep Dive](../02-lcm-deepdive/philosophy.md) - Understand the architecture
