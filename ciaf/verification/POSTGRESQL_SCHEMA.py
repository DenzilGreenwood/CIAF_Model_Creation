"""
PostgreSQL Schema for CIAF Verification Service

Database design for proof storage and verification.
Deploy with Alembic migrations in production.

Created: 2025-03-13
Author: Denzil James Greenwood
"""

POSTGRESQL_SCHEMA = """
-- ========================================================================
-- OUTPUT TAGS TABLE
-- ========================================================================
-- Stores all output tags with complete metadata
-- Indexes optimized for tag lookup and organization queries

CREATE TABLE output_tags (
    tag_id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    output_content_hash VARCHAR(64) NOT NULL UNIQUE,
    inference_receipt_id VARCHAR(100) NOT NULL,

    -- Output classification
    inference_type VARCHAR(30) NOT NULL,  -- "agent_orchestrated" or "direct_model"
    model_name VARCHAR(100),                -- For direct model inference
    agent_ids JSONB NOT NULL,               -- List of agent IDs (for agent orchestration)

    -- Organizational context
    organization_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    -- Governance metadata
    policies_applied JSONB NOT NULL,        -- List of policy IDs
    risk_level VARCHAR(20) NOT NULL,        -- "low", "medium", "high", "critical"

    -- Task batch reference
    task_batch_id VARCHAR(36),
    task_batch_merkle_root VARCHAR(64),
    task_batch_proof JSONB,                 -- Merkle proof as JSON array

    -- Org batch reference
    org_batch_id VARCHAR(100),
    org_batch_merkle_root VARCHAR(64),
    org_batch_proof JSONB,

    -- Verification status
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (session_id) REFERENCES agent_sessions(session_id),
    FOREIGN KEY (task_batch_id) REFERENCES task_batches(task_batch_id),
    FOREIGN KEY (org_batch_id) REFERENCES org_batch_windows(window_id)
);

-- Indexes for fast lookup
CREATE INDEX idx_output_tags_by_session ON output_tags(session_id);
CREATE INDEX idx_output_tags_by_org ON output_tags(organization_id);
CREATE INDEX idx_output_tags_by_content_hash ON output_tags(output_content_hash);
CREATE INDEX idx_output_tags_by_model ON output_tags(model_name);
CREATE INDEX idx_output_tags_verified ON output_tags(is_verified);
CREATE INDEX idx_output_tags_risk ON output_tags(risk_level);


-- ========================================================================
-- TASK BATCHES TABLE
-- ========================================================================
-- Stores task batch metadata and merkle tree root
-- Links outputs to batches via task_batch_id

CREATE TABLE task_batches (
    task_batch_id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    organization_id VARCHAR(100) NOT NULL,

    -- Batch metadata
    status VARCHAR(20) NOT NULL,            -- "success", "failure", "partial"
    content_hash VARCHAR(64) NOT NULL,      -- Deterministic hash of batch contents

    -- Merkle tree
    merkle_root VARCHAR(64),                -- Root hash of outputs in batch
    merkle_tree_leaves JSONB,               -- Content hashes of outputs

    -- Timing
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_ms DECIMAL(10, 2),

    -- Output tracking
    output_tag_count INTEGER DEFAULT 0,

    -- Org batch reference
    org_batch_id VARCHAR(100),

    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (session_id) REFERENCES agent_sessions(session_id),
    FOREIGN KEY (org_batch_id) REFERENCES org_batch_windows(window_id)
);

CREATE INDEX idx_task_batches_by_session ON task_batches(session_id);
CREATE INDEX idx_task_batches_by_org ON task_batches(organization_id);
CREATE INDEX idx_task_batches_by_status ON task_batches(status);
CREATE INDEX idx_task_batches_merkle_root ON task_batches(merkle_root);


-- ========================================================================
-- ORGANIZATION BATCH WINDOWS TABLE
-- ========================================================================
-- Time-based batches (6-hour windows) of task batches
-- Creates organization-level merkle tree

CREATE TABLE org_batch_windows (
    window_id VARCHAR(100) PRIMARY KEY,
    organization_id VARCHAR(100) NOT NULL,

    -- Time window
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,

    -- Contents
    task_batch_ids JSONB NOT NULL,          -- List of task_batch_ids in window
    task_batch_count INTEGER NOT NULL,

    -- Merkle tree
    merkle_root VARCHAR(64) NOT NULL,       -- Root of all task batches in window
    merkle_tree_leaves JSONB,               -- Content hashes of task batches

    -- Status
    status VARCHAR(20) NOT NULL,            -- "pending", "completed", "closed"

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(organization_id, window_start)
);

CREATE INDEX idx_org_batch_by_org ON org_batch_windows(organization_id);
CREATE INDEX idx_org_batch_by_window_start ON org_batch_windows(window_start);
CREATE INDEX idx_org_batch_merkle_root ON org_batch_windows(merkle_root);
CREATE INDEX idx_org_batch_status ON org_batch_windows(status);


-- ========================================================================
-- AGENT ACTIONS TABLE (AUDIT TRAIL)
-- ========================================================================
-- Detailed log of each agent action for audit trail

CREATE TABLE agent_actions (
    action_id VARCHAR(36) PRIMARY KEY,
    task_batch_id VARCHAR(36) NOT NULL,

    -- Agent identification
    agent_id VARCHAR(100) NOT NULL,

    -- Action details
    action_type VARCHAR(50) NOT NULL,       -- "inference", "analysis", "decision"
    timestamp TIMESTAMP NOT NULL,

    -- Inputs and outputs
    input_hash VARCHAR(64),
    output_hash VARCHAR(64),

    -- Governance
    policies_enforced JSONB,                -- List of policy IDs enforced
    risk_level VARCHAR(20),                 -- Risk level for this action

    -- Status
    status VARCHAR(20) NOT NULL,            -- "success", "failure", "partial"
    duration_ms DECIMAL(10, 2),
    error_message TEXT,

    -- Metadata
    metadata JSONB,

    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (task_batch_id) REFERENCES task_batches(task_batch_id)
);

CREATE INDEX idx_agent_actions_by_batch ON agent_actions(task_batch_id);
CREATE INDEX idx_agent_actions_by_agent ON agent_actions(agent_id);
CREATE INDEX idx_agent_actions_by_timestamp ON agent_actions(timestamp);


-- ========================================================================
-- SESSIONS TABLE
-- ========================================================================
-- User sessions (referenced by output_tags and task_batches)

CREATE TABLE agent_sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    organization_id VARCHAR(100) NOT NULL,

    -- Timing
    created_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,

    -- Metadata
    session_metadata JSONB
);

CREATE INDEX idx_sessions_by_user ON agent_sessions(user_id);
CREATE INDEX idx_sessions_by_org ON agent_sessions(organization_id);


-- ========================================================================
-- VERIFICATION CACHE TABLE (optional)
-- ========================================================================
-- Cache for frequently verified tags (optional - use Redis instead in production)

CREATE TABLE verification_cache (
    tag_id VARCHAR(36) PRIMARY KEY,
    last_verified TIMESTAMP NOT NULL,
    verification_result JSONB NOT NULL,
    hits INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (tag_id) REFERENCES output_tags(tag_id)
);

CREATE INDEX idx_cache_last_verified ON verification_cache(last_verified);


-- ========================================================================
-- STATS VIEW
-- ========================================================================
-- Aggregate view for organization statistics

CREATE VIEW org_verification_stats AS
SELECT
    o.organization_id,
    COUNT(DISTINCT t.tag_id) as total_tags,
    SUM(CASE WHEN t.is_verified THEN 1 ELSE 0 END) as verified_tags,
    SUM(CASE WHEN t.risk_level = 'high' THEN 1 ELSE 0 END) as high_risk_tags,
    SUM(CASE WHEN t.risk_level = 'critical' THEN 1 ELSE 0 END) as critical_tags,
    COUNT(DISTINCT w.window_id) as batch_windows,
    MAX(t.created_at) as last_output
FROM output_tags t
LEFT JOIN org_batch_windows w ON t.org_batch_id = w.window_id
GROUP BY o.organization_id;
"""

SETUP_INSTRUCTIONS = """
# PostgreSQL Setup for CIAF Verification Service

## Installation (Production)

### 1. Create Database and User

```sql
-- Connect as postgres user
sudo -u postgres psql

-- Create database
CREATE DATABASE ciaf_proofs;

-- Create user with privileges
CREATE USER ciaf_verification WITH PASSWORD 'secure_password_here';
GRANT CREATE ON DATABASE ciaf_proofs TO ciaf_verification;
\\c ciaf_proofs
GRANT ALL PRIVILEGES ON SCHEMA public TO ciaf_verification;
```

### 2. Run Schema

```bash
# Install Alembic for migrations (production)
pip install alembic sqlalchemy psycopg2-binary

# Initialize migrations
alembic init alembic
# Edit alembic/env.py to set SQLAlchemy URL
# Run migrations
alembic upgrade head

# Or run schema directly (development)
psql -U ciaf_verification -d ciaf_proofs < schema.sql
```

### 3. Connection String (Production)

```python
DATABASE_URL = "postgresql+asyncpg://ciaf_verification:password@localhost:5432/ciaf_proofs"
```

## Performance Tuning (Production)

### Indexes
All tables have appropriate indexes for:
- Session lookups
- Organization queries
- Merkle root searches
- Verification status checks
- Risk level filtering

### Connection Pooling
```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,              # Connections to keep open
    max_overflow=10,           # Additional connections if needed
    pool_pre_ping=True,        # Test connections before use
    pool_recycle=3600,         # Recycle connections after 1 hour
)
```

### Caching Strategy
1. **Output tags**: Redis cache (5-minute TTL)
2. **Merkle proofs**: In-memory cache (updated on new batch)
3. **Organization stats**: Redis cache (hourly)

### Backup Strategy
```bash
# Daily full backup
pg_dump -U ciaf_verification ciaf_proofs | gzip > backup_$(date +%Y%m%d).sql.gz

# Continuous archiving (WAL)
wal_level = replica
archive_mode = on
```

## Monitoring (Production)

### Key Metrics
- Query performance (slow query log)
- Connection pool usage
- Table growth rate
- Verification success rate

### Health Checks
```bash
# Connection test
psql -U ciaf_verification -d ciaf_proofs -c "SELECT 1"

# Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Development Setup (Local)

```bash
# Install PostgreSQL locally
brew install postgresql@14  # macOS
apt-get install postgresql  # Linux
choco install postgresql    # Windows

# Start service
brew services start postgresql

# Create local database
createdb ciaf_proofs

# Load schema
psql ciaf_proofs < schema.sql

# Connect
psql ciaf_proofs
```

## Data Retention Policy

### Default Retention
- Output tags: 7 years (regulatory requirement)
- Task batches: 7 years
- Org batch windows: 7 years
- Agent actions: 7 years
- Verification cache: 24 hours

### Archive Strategy
After 3 years, move to cold storage (S3/Glacier):
```sql
-- Archive old data
COPY (SELECT * FROM output_tags WHERE created_at < NOW() - INTERVAL '3 years')
TO PROGRAM 'aws s3 cp - s3://ciaf-archive/output_tags_2022.csv'
WITH (FORMAT CSV);

-- Delete from hot storage (after verification)
DELETE FROM output_tags WHERE created_at < NOW() - INTERVAL '3 years';
```
"""

if __name__ == "__main__":
    print("PostgreSQL Schema for CIAF Verification Service")
    print("=" * 80)
    print()
    print(POSTGRESQL_SCHEMA)
    print()
    print("=" * 80)
    print(SETUP_INSTRUCTIONS)
