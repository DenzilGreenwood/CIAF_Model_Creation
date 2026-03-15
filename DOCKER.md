# 🐳 CIAF Docker Guide - Complete Stack

Run the entire CIAF system locally with Docker: Frontend, APIs, Database, and Cache.

## Quick Start

### Windows
```cmd
docker-setup.bat
```

### Mac/Linux
```bash
chmod +x docker-setup.sh
./docker-setup.sh
```

### All Platforms
```bash
docker-compose up -d
```

---

## What Gets Started

| Service | Port | Purpose |
|---------|------|---------|
| **Frontend** | 3000 | React UI for Artificial Intelligence Evidence Vault |
| **Vault API** | 8002 | Cryptographic proof custody API |
| **Verification Service** | 8001 | Output tag verification & compliance |
| **PostgreSQL** | 5432 | Primary database for proofs |
| **Redis** | 6379 | Cache for performance |

---

## Accessing Services

### 🖥️ Frontend (React Dashboard)
```
URL: http://localhost:3002
```
- View proofs
- Verify outputs
- Check compliance
- Monitor statistics

### 🔌 Vault API (REST)
```
Base URL: http://localhost:8002
Health Check: http://localhost:8002/health
```

### 📊 Verification Service
```
Base URL: http://localhost:8001
Health Check: http://localhost:8001/health
```

### 📦 Database (PostgreSQL)
```
Host: localhost
Port: 5432
User: ciaf_verification
Password: ciaf_secure_password_dev
Database: ciaf_proofs
```

```bash
# Connect with psql
psql -h localhost -U ciaf_verification -d ciaf_proofs

# Or with Docker
docker-compose exec postgres psql -U ciaf_verification -d ciaf_proofs
```

### 💾 Cache (Redis)
```
Host: localhost
Port: 6379
```

```bash
# Connect with redis-cli
redis-cli

# Or with Docker
docker-compose exec redis redis-cli
```

---

## Common Commands

### Start Services
```bash
# Start in background
docker-compose up -d

# Start with logs visible
docker-compose up
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f vault
docker-compose logs -f verification-service
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100
```

### Check Status
```bash
# List running containers
docker-compose ps

# Container resources
docker stats

# Individual container
docker-compose logs vault | head -20
```

### Stop Services
```bash
# Stop all (keeps data)
docker-compose down

# Stop and remove everything (wipes data)
docker-compose down -v

# Stop specific service
docker-compose stop vault
```

### Rebuild Images
```bash
# Rebuild all
docker-compose build --no-cache

# Rebuild specific
docker-compose build --no-cache vault
```

### Execute Commands
```bash
# Run command in container
docker-compose exec postgres psql -U ciaf_verification -d ciaf_proofs

# Get shell access
docker-compose exec vault /bin/bash

# Run one-off command
docker-compose run vault python -m pytest api.test.py
```

---

## API Examples

### 1. Health Check
```bash
curl http://localhost:8002/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Artificial Intelligence Evidence Vault",
  "version": "1.0.0"
}
```

### 2. Submit Proof
```bash
curl -X POST http://localhost:8002/submit \
  -H "Authorization: Bearer test-api-key-org-1" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "AI model output",
    "agent_ids": ["agent-1"],
    "policies_applied": ["policy-1"],
    "timestamp": "2026-03-14T00:00:00Z"
  }'
```

### 3. Verify Proof
```bash
curl http://localhost:8002/verify/proof-id-123 \
  -H "Authorization: Bearer test-api-key-org-1"
```

### 4. Complete Example
```bash
python examples/api_client_example.py
```

---

## Database Management

### Access Database
```bash
# From host
psql -h localhost -U ciaf_verification -d ciaf_proofs

# From Docker
docker-compose exec postgres psql -U ciaf_verification -d ciaf_proofs
```

### Useful Queries
```sql
-- Check tables
\dt

-- Count proofs
SELECT COUNT(*) FROM proofs;

-- View recent proofs
SELECT proof_id, created_at, read_count FROM proofs ORDER BY created_at DESC LIMIT 10;

-- Check audit trail
SELECT action, timestamp FROM audit_log ORDER BY timestamp DESC LIMIT 20;
```

---

## Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs vault

# Rebuild images
docker-compose build --no-cache vault

# Restart service
docker-compose restart vault
```

### Port Already in Use
```bash
# Find what's using port
lsof -i :8002

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Database Connection Failed
```bash
# Wait longer for PostgreSQL
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres

# Check if healthy
docker-compose ps postgres
```

### Cache Issues
```bash
# Flush Redis cache
docker-compose exec redis redis-cli FLUSHALL

# Check Redis status
docker-compose exec redis redis-cli INFO
```

### Docker Daemon Not Running
```
Error: Cannot connect to Docker daemon

# Start Docker Desktop or daemon
# On Linux: sudo systemctl start docker
# On Mac: Start Docker Desktop app
# On Windows: Start Docker Desktop app
```

---

## Performance Optimization

### Resource Limits
The docker-compose.yml already has optimal settings:
- PostgreSQL: 1GB memory
- Redis: 512MB memory
- Vault: 512MB memory

### Connection Pooling
- PostgreSQL: 10 connections, 5 overflow
- Redis: Auto connection pooling

### Caching
- Response cache: 5 minutes (Redis)
- Database query cache: Built-in
- API response caching: Enabled by default

---

## Security Features

### API Authentication
```
Header: Authorization: Bearer <api-key>
Key: test-api-key-org-1 (development only)
```

### Network
```
Services communicate via internal network
No services exposed to internet by default
All traffic encrypted in transit (TLS optional)
```

### Database
```
Default credentials (dev only):
User: ciaf_verification
Password: ciaf_secure_password_dev

⚠️  CHANGE IN PRODUCTION!
```

---

## Development Tips

### Hot Reload
```bash
# Code changes auto-reload:
# - API changes: Automatic (uvicorn reload)
# - Frontend: Auto-rebuild in Docker
# - Database: Changes persist in volume

# Watch logs
docker-compose logs -f vault
```

### Debug Mode
```bash
# Drop into shell
docker-compose exec vault /bin/bash

# Run tests
docker-compose exec vault pytest api.test.py -v

# Check Python version
docker-compose exec vault python --version
```

### Data Persistence
```bash
# Data persists in volumes:
volumes:
  postgres_data     # PostgreSQL data
  redis_data        # Redis memory snapshots

# To reset data:
docker-compose down -v
docker-compose up -d
```

---

## Production Considerations

### Before Going Live
- [ ] Change database credentials
- [ ] Change API keys to strong values
- [ ] Use environment file (.env)
- [ ] Enable TLS/SSL encryption
- [ ] Set up backups for PostgreSQL
- [ ] Monitor with Prometheus (optional)
- [ ] Enable authentication on Redis
- [ ] Review security policies

### Scaling
```bash
# Run multiple instances
docker-compose up -d --scale vault=3

# Use load balancer
# Add nginx or similar
```

### Monitoring
```bash
# Prometheus already configured
# Access: http://localhost:9090

# Enable monitoring
docker-compose --profile monitoring up -d
```

---

## Useful Links

- Docker: https://www.docker.com
- Docker Compose: https://docs.docker.com/compose
- PostgreSQL: https://www.postgresql.org
- Redis: https://redis.io
- FastAPI: https://fastapi.tiangolo.com

---

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify services: `docker-compose ps`
3. Check connectivity: `curl http://localhost:8002/health`
4. See troubleshooting section above

---

**Status:** ✅ Ready to Run
**Last Updated:** 2026-03-14
