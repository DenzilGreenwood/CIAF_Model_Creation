# PostgreSQL Migration Strategy

**Complete guide for migrating from SQLite development to PostgreSQL production.**

---

## Overview

CIAF uses **Alembic** for schema versioning and database migrations. This document covers:
- Development workflow (SQLite → Testing)
- Production deployment (PostgreSQL)
- Zero-downtime migration path
- Rollback procedures

---

## Architecture

### SQLite (Development)
- File-based, no server needed
- Fast iteration, all-in-one setup
- Used with: `ciaf/verification/proof_store.py` (local SQLite)

### PostgreSQL (Production)
- Concurrent connections, row-level locking
- ACID compliance, advanced monitoring
- Connection pooling, replication support
- Used with: `ciaf/verification/api.py` (async psycopg2/asyncpg)

---

## Database Schema

The proof store schema includes:

| Table | Purpose | Rows (Est.) |
|-------|---------|------------|
| `output_tags` | Primary proof records | 10M+ (7-year retention) |
| `task_batches` | Merkle tree batches | 100K+ |
| `org_batch_windows` | Organization windows | 50K+ |
| `agent_actions` | Audit trail (INSERT-only) | 100M+ |
| `verification_events` | Read verification log | 1M+ |

**Key Constraints:**
- `output_tags.tag_id` - PRIMARY KEY (UUID)
- `output_tags.output_content_hash` - UNIQUE (SHA-256)
- `org_batch_windows.created_at` - INDEX (org queries)
- `agent_actions` - INSERT-ONLY (WORM guarantee)

---

## Migration Workflow

### Phase 0: Set Up PostgreSQL (Pre-Deployment)

```bash
# Local development (if testing locally)
brew install postgresql@14  # macOS
apt-get install postgresql  # Linux
choco install postgresql    # Windows (via Chocolatey)

# Start service
brew services start postgresql@14

# Or use Docker for quick testing
docker run --name ciaf-postgres \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=ciaf_proofs \
  -p 5432:5432 \
  postgres:14-alpine
```

### Phase 1: Update Alembic Configuration

Edit `alembic.ini`:

```ini
# sqlalchemy.url = sqlite:///./ciaf_proofs.db

# Change to:
sqlalchemy.url = postgresql+asyncpg://ciaf_user:password@localhost:5432/ciaf_proofs
```

Or use environment variable:

```bash
export SQLALCHEMY_URL="postgresql://ciaf_user:password@localhost:5432/ciaf_proofs"
```

### Phase 2: Create Initial Migration

```bash
# Auto-generate migration from current SQLite schema
alembic revision --autogenerate -m "Initial schema from SQLite"

# This creates: ciaf/migrations/versions/001_initial_schema.py
```

### Phase 3: Review and Test Migration

```bash
# Review the generated migration
cat ciaf/migrations/versions/001_initial_schema.py

# Test migration on staging database
alembic upgrade head

# If successful:
alembic downgrade base  # Test rollback
alembic upgrade head    # Test upgrade again
```

### Phase 4: Production Migration (Zero-Downtime)

**Option A: During Maintenance Window**

```bash
# 1. Stop all write operations
docker-compose down verification-service vault-service

# 2. Export current data from SQLite
sqlite3 ~/.ciaf/ciaf_proofs.db ".backup /tmp/backup.sqlite"

# 3. Import into PostgreSQL
# Using migration tool or SQL dumps
psql -U ciaf_user -d ciaf_proofs -f /path/to/schema.sql

# 4. Run Alembic migrations
alembic upgrade head

# 5. Verify data integrity
# See verification script below

# 6. Restart services
docker-compose up -d verification-service vault-service
```

**Option B: Blue-Green Deployment**

```bash
# 1. Deploy NEW stack with PostgreSQL
docker-compose -f docker-compose.yml -f docker-compose.postgres.yml up -d

# 2. Run migrations on new stack
alembic upgrade head

# 3. Sync data from SQLite to PostgreSQL
python scripts/sync_sqlite_to_postgres.py

# 4. Run verification tests
pytest tests/test_integration.py::test_postgres_migration -v

# 5. Switch traffic to new stack (DNS/LB change)

# 6. Keep old SQLite stack running for 24h rollback window
```

---

## Verification Script

After migration, verify data integrity:

```python
# scripts/verify_migration.py
import psycopg2
from pathlib import Path

def verify_migration():
    """Verify PostgreSQL migration completed successfully."""

    conn = psycopg2.connect(
        dbname="ciaf_proofs",
        user="ciaf_user",
        password="password",
        host="localhost"
    )

    cursor = conn.cursor()

    # Check table counts
    checks = {
        "output_tags": "SELECT COUNT(*) FROM output_tags",
        "task_batches": "SELECT COUNT(*) FROM task_batches",
        "agent_actions": "SELECT COUNT(*) FROM agent_actions",
    }

    print("Migration Verification Results:")
    print("=" * 60)

    for table, query in checks.items():
        cursor.execute(query)
        count = cursor.fetchone()[0]
        print(f"✓ {table}: {count:,} rows")

    # Check indexes exist
    cursor.execute("""
        SELECT indexname FROM pg_indexes
        WHERE tablename='output_tags'
    """)
    indexes = [row[0] for row in cursor.fetchall()]
    print(f"✓ Indexes created: {len(indexes)}")

    # Check constraints exist
    cursor.execute("""
        SELECT constraint_name FROM information_schema.table_constraints
        WHERE table_name='output_tags'
    """)
    constraints = cursor.fetchall()
    print(f"✓ Constraints: {len(constraints)}")

    cursor.close()
    conn.close()

    print("=" * 60)
    print("✅ Migration verification passed!")

if __name__ == "__main__":
    verify_migration()
```

---

## Connection Pooling (Production)

Use `sqlalchemy.pool.QueuePool` for efficient connection reuse:

```python
# ciaf/verification/api.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=QueuePool,
    pool_size=20,           # Keep 20 connections in pool
    max_overflow=10,        # Allow 10 overflow connections
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_pre_ping=True,     # Test connection before using
)
```

---

## Disaster Recovery

### Backup Strategy

```bash
# Full backup (daily, automated)
PGPASSWORD=password pg_dump -U ciaf_user -d ciaf_proofs | \
  gzip > /backups/ciaf_proofs_$(date +%Y%m%d).sql.gz

# Incremental backup (hourly, WAL archiving)
# Configure in postgresql.conf:
# wal_level = replica
# archive_mode = on
# archive_command = 'cp %p /archive/%f'
```

### Restore from Backup

```bash
# Restore full dump
gunzip < /backups/ciaf_proofs_20260315.sql.gz | \
  psql -U ciaf_user -d ciaf_proofs

# Point-in-time recovery (requires WAL archives)
pg_restore -d ciaf_proofs \
  --recovery-target-time '2026-03-15 14:30:00' \
  /path/to/backup.sql
```

### Rollback Procedure

```bash
# If migration fails:
alembic downgrade base

# If rollback fails:
# 1. Restore from pre-migration backup
psql -U ciaf_user -c "DROP DATABASE ciaf_proofs"
gunzip < /backups/ciaf_proofs_pre_migration.sql.gz | \
  psql -U ciaf_user

# 2. Revert services to SQLite
docker-compose down
docker-compose up -d  # Falls back to SQLite
```

---

## Environment Configuration

### Development (.env)

```bash
# Uses SQLite (file-based, no setup needed)
DATABASE_URL=sqlite:///./ciaf_proofs.db
```

### Staging (.env.staging)

```bash
# PostgreSQL on managed cloud provider
DATABASE_URL=postgresql+asyncpg://ciaf_user:password@staging-db.internal:5432/ciaf_proofs
```

### Production (.env.production)

```bash
# High-availability PostgreSQL with replication
DATABASE_URL=postgresql+asyncpg://ciaf_user:password@prod-db-primary.internal:5432/ciaf_proofs
DATABASE_REPLICA_URL=postgresql+asyncpg://ciaf_user:password@prod-db-replica.internal:5432/ciaf_proofs

# Connection pooling
POOL_SIZE=50
MAX_OVERFLOW=20
POOL_RECYCLE=3600
```

---

## Monitoring & Maintenance

### Connection Pool Health

```sql
-- Check active connections
SELECT datname, usename, count(*) as connections
FROM pg_stat_activity
GROUP BY datname, usename;

-- Check connection limits
SHOW max_connections;
SHOW superuser_reserved_connections;
```

### Slow Queries

```sql
-- Enable query logging (production)
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries >1s

-- Query performance
EXPLAIN ANALYZE SELECT * FROM output_tags WHERE organization_id = 'org-1';
```

### Vacuum & Maintenance

```bash
# Automatic vacuum (configured in PostgreSQL)
# Manual vacuum for optimization
psql -U ciaf_user -d ciaf_proofs -c "VACUUM ANALYZE;"

# Reindex (if performance degrades)
psql -U ciaf_user -d ciaf_proofs -c "REINDEX INDEX CONCURRENTLY idx_output_tags_org_id;"
```

---

## Testing

### Integration Tests with PostgreSQL

```bash
# Run tests against PostgreSQL
pytest tests/test_integration.py -v -k postgresql

# Performance tests
pytest tests/test_performance.py -v --database=postgresql
```

### Data Validation

```bash
# Compare SQLite vs PostgreSQL row counts
python scripts/verify_row_counts.py

# Check data consistency
python scripts/validate_checksums.py
```

---

## Timeline & Checklist

### Week 1: Preparation
- [ ] Set up PostgreSQL test instance
- [ ] Review Alembic migrations
- [ ] Train team on rollback procedure
- [ ] Create backup strategy

### Week 2: Staging
- [ ] Test migration on staging
- [ ] Run performance benchmarks
- [ ] Verify monitoring/alerting
- [ ] Document any issues

### Week 3: Production
- [ ] Schedule maintenance window (off-peak)
- [ ] Create pre-migration backup
- [ ] Execute blue-green deployment OR maintenance window
- [ ] Run verification script
- [ ] Monitor for 24h

### Post-Migration
- [ ] Disable SQLite fallback (after 30 days)
- [ ] Set up automated backups and WAL archiving
- [ ] Monitor query performance monthly
- [ ] Plan read replicas (optional, for HA)

---

## Reference

### Alembic Commands

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Upgrade (move forward)
alembic upgrade head

# Downgrade (rollback)
alembic downgrade -1

# Check history
alembic history --verbose

# Current version
alembic current
```

### PostgreSQL Connection String Format

```
postgresql+asyncpg://user:password@host:port/database
postgresql://user:password@host/database  # synchronous
```

---

**Status**: ✅ Ready for Production Migration

**Last Updated**: 2026-03-15
**Author**: CIAF Engineering Team + Claude AI
