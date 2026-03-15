# 🚀 Local Development Setup Guide

**Complete guide to running CIAF locally for development and testing.**

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 4GB | 8GB+ |
| **Disk Space** | 5GB | 10GB (with Docker images) |
| **Python** | 3.10 | 3.10+ |
| **Node.js** | 18 | 18+, 20+ |
| **Docker** | 20.10 | Latest (Docker Desktop recommended) |

---

## ⚡ QUICKEST START: Docker (5 minutes)

### Windows

```bash
# 1. Open PowerShell as Administrator and navigate to project
cd CIAF_Model_Creation

# 2. Create environment file
echo "DB_PASSWORD=secure_password_123" > .env

# 3. Run one-line setup
.\docker-setup.bat

# 4. Start all services
docker-compose up -d

# 5. Verify services are running
docker-compose ps

# 6. Access applications
# Frontend:  http://localhost:3000
# API Docs:  http://localhost:8001/docs
# Vault:     http://localhost:8002/docs
# Metrics:   http://localhost:9090
# Grafana:   http://localhost:3001
```

### Mac/Linux

```bash
# 1. Navigate to project
cd CIAF_Model_Creation

# 2. Create environment file
echo "DB_PASSWORD=secure_password_123" > .env

# 3. Run setup script
chmod +x docker-setup.sh
./docker-setup.sh

# 4. Start all services
docker-compose up -d

# 5. Verify services
docker-compose ps

# 6. Access applications (same URLs as Windows above)
```

---

## 🏗️ What Gets Started (Docker)

| Service | Port | Technology | Health Check |
|---------|------|-----------|--------------|
| **Frontend** | 3000 | React + TypeScript | http://localhost:3000 |
| **Verification API** | 8001 | FastAPI + SQLite | http://localhost:8001/health |
| **AI Evidence Vault** | 8002 | FastAPI + SQLite | http://localhost:8002/health |
| **PostgreSQL** | 5432 | Database | `docker logs ciaf-postgres` |
| **Redis** | 6379 | Cache | `redis-cli ping` |
| **Prometheus** | 9090 | Metrics | http://localhost:9090 |
| **Grafana** | 3001 | Dashboards | http://localhost:3001 |
| **Loki** | 3100 | Logs | Internal only |
| **Jaeger** | 16686 | Tracing | http://localhost:16686 |

---

## 💻 Alternative: Native Development (No Docker)

Use this approach if you prefer running services directly on your machine.

### Backend Setup

#### 1. Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

#### 2. Install Dependencies

```bash
# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Or install from pyproject.toml
pip install -e ".[dev]"

# Key packages needed:
# - fastapi
# - uvicorn
# - sqlalchemy
# - psycopg2-binary (if using PostgreSQL)
# - pydantic
# - cryptography
```

#### 3. Start Backend Services

**Option A: Local SQLite (Easiest)**
```bash
# No database setup needed, uses local file
python -m uvicorn ciaf.verification.api:app --reload --port 8001

# In another terminal
python -m uvicorn ciaf.vault.api:app --reload --port 8002
```

**Option B: PostgreSQL (Production-like)**
```bash
# Install PostgreSQL locally, then create database
# Windows: Use PostgreSQL installer
# Mac: brew install postgresql
# Linux: apt-get install postgresql

# Start PostgreSQL
pg_ctl start  # or use system service

# Create database
createdb -U postgres ciaf_proofs

# Update connection string in code
# Then start
python -m uvicorn ciaf.verification.api:app --reload --port 8001
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Frontend will be at http://localhost:5173 (or URL shown in terminal)

# In separate terminal, run tests
npm run test

# Or E2E tests
npm run test:e2e
```

---

## 🧪 Running Tests

### Backend Tests (All at once)

```bash
# Run all tests with coverage
pytest tests/ -v --cov=ciaf --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test
pytest tests/test_auth.py::TestTokenGeneration::test_token_has_expiration -v

# Run with specific marker
pytest -m "unit" -v  # Only unit tests
pytest -m "integration" -v  # Only integration tests
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm run test

# Run with coverage
npm run test -- --coverage

# Run E2E tests
npm run test:e2e

# Run specific test file
npm run test -- Dashboard.test.tsx
```

### Quick Test Scripts (Pre-configured)

```bash
# Windows
test-backend.bat
test-frontend.bat

# Mac/Linux
./test-backend.sh
./test-frontend.sh
```

---

## 📊 Accessing Services

### Web Interfaces

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| **Frontend** | http://localhost:3000 | None | Web UI |
| **API Docs** | http://localhost:8001/docs | None | Interactive API testing |
| **Vault Docs** | http://localhost:8002/docs | None | Vault API testing |
| **Prometheus** | http://localhost:9090 | None | Metrics explorer |
| **Grafana** | http://localhost:3001 | admin/admin | Dashboards |
| **Jaeger** | http://localhost:16686 | None | Distributed tracing |

### Command Line

```bash
# Check backend health
curl http://localhost:8001/health

# Submit a proof (Verification API)
curl -X POST http://localhost:8001/verify \
  -H "Content-Type: application/json" \
  -d '{"content": "test output", "model_version": "1.0.0"}'

# Check vault health
curl http://localhost:8002/health

# Connect to PostgreSQL
psql -U ciaf_verification -d ciaf_proofs -h localhost

# Query proofs
SELECT proof_id, status, created_at FROM proofs LIMIT 5;

# Connect to Redis
redis-cli
> ping
PONG
```

---

## 🔧 Common Development Tasks

### Hot Reload

**Backend:**
```bash
# Uvicorn auto-reloads when you change files
python -m uvicorn ciaf.verification.api:app --reload
```

**Frontend:**
```bash
# Vite auto-reloads when you change files
npm run dev
```

### Database Operations

```bash
# View schema
psql -U ciaf_verification -d ciaf_proofs -c "\dt"

# Export data
pg_dump -U ciaf_verification ciaf_proofs > backup.sql

# Import data
psql -U ciaf_verification ciaf_proofs < backup.sql

# Reset database (careful!)
psql -U postgres -c "DROP DATABASE ciaf_proofs;"
psql -U postgres -c "CREATE DATABASE ciaf_proofs;"
```

### Viewing Logs

```bash
# Docker logs
docker-compose logs -f verification-service
docker-compose logs -f vault-service
docker-compose logs -f postgres
docker-compose logs -f redis

# Tail specific service
docker-compose logs --tail 100 verification-service
```

### Rebuild Docker Images

```bash
# Rebuild after code changes
docker-compose build

# Rebuild specific service
docker-compose build verification-service

# Rebuild and restart
docker-compose up -d --build
```

---

## 🚨 Troubleshooting

### Docker Issues

**Services won't start:**
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Reset everything (WARNING: deletes data)
docker-compose down -v
docker system prune -a
docker-compose up -d
```

**Port already in use:**
```bash
# Windows - find and kill process
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux - find and kill process
lsof -i :3000
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -U ciaf_verification -d ciaf_proofs -h localhost -c "SELECT 1;"

# Check PostgreSQL logs
docker-compose logs postgres

# Verify credentials in .env
cat .env
```

### Frontend Not Loading

```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules
npm install
npm run dev

# Check if port 5173 is in use
lsof -i :5173
```

### Backend Import Errors

```bash
# Ensure virtual environment is activated
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 🎯 Demo Workflows

### Run MVP Multi-Agent Demo

```bash
# Docker setup first, then:
./run_mvp.sh

# Or
python examples/mvp_demo.py

# Output shows:
# - Banking workflow with 4 agents
# - Healthcare workflow with 3 agents
# - Cross-domain collaboration
# - All outputs tagged and verified
```

### Test Individual Components

```bash
# Authentication flow
pytest tests/test_auth.py -v

# Cryptographic proofs
pytest tests/test_lcm.py -v

# API endpoints
pytest tests/test_api.py -v

# Integration workflow
pytest tests/test_integration.py -v
```

---

## 📝 Environment Variables

Create a `.env` file in project root:

```bash
# Database
DB_USER=ciaf_verification
DB_PASSWORD=secure_password_123
DB_NAME=ciaf_proofs
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379

# API
API_PORT=8001
VAULT_PORT=8002

# Security
SECRET_KEY=your-secret-key-here-min-32-chars
JWT_EXPIRATION_HOURS=24

# Logging
LOG_LEVEL=INFO

# Features
ENABLE_VAULT=true
ENABLE_METRICS=true
```

---

## 🔐 Security Notes for Local Development

- ⚠️ Never commit `.env` files with real secrets
- Use strong passwords even in development
- Keep Docker images updated: `docker-compose pull`
- Don't expose `8001`, `8002` to public internet
- Use HTTPS in production (included in deployment config)

---

## 📚 Additional Resources

| Document | Purpose |
|----------|---------|
| [API_REFERENCE.md](API_REFERENCE.md) | Complete API endpoint documentation |
| [README_VAULT.md](README_VAULT.md) | AI Evidence Vault features & usage |
| [DOCKER.md](DOCKER.md) | Docker & deployment deep dive |
| [ciaf/verification/QUICK_START_GUIDE.md](ciaf/verification/QUICK_START_GUIDE.md) | Verification service setup |

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] `docker-compose ps` shows all services running
- [ ] `curl http://localhost:8001/health` returns 200
- [ ] `curl http://localhost:3000` loads frontend
- [ ] `http://localhost:8001/docs` shows API documentation
- [ ] Backend tests pass: `pytest tests/ -q`
- [ ] Frontend tests pass: `npm test`
- [ ] Can submit proof via API
- [ ] Prometheus scraping metrics
- [ ] Grafana dashboards accessible

---

## 🆘 Getting Help

1. **Check logs first**:
   ```bash
   docker-compose logs [service-name]
   ```

2. **Test connectivity**:
   ```bash
   curl -v http://localhost:8001/health
   ```

3. **Reset environment**:
   ```bash
   docker-compose down -v
   rm -rf venv
   docker-compose up -d
   ```

4. **Review documentation**:
   - API docs: http://localhost:8001/docs
   - Architecture: See `README.md`
   - Security: See `ciaf/SECURITY.md`

---

**Last Updated:** 2026-03-15
**Status:** ✅ Production Ready

For questions, refer to the main [README.md](README.md) or open an issue on GitHub.
