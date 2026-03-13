# CIAF Verification Microservice - Production Deployment Runbook

Comprehensive guide for deploying the CIAF Verification Microservice to production environments.

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Infrastructure Setup](#infrastructure-setup)
3. [Security Configuration](#security-configuration)
4. [Database Deployment](#database-deployment)
5. [Service Deployment](#service-deployment)
6. [Monitoring & Alerting](#monitoring--alerting)
7. [Backup & Recovery](#backup--recovery)
8. [Performance Tuning](#performance-tuning)
9. [Troubleshooting](#troubleshooting)
10. [Incident Response](#incident-response)

---

## Pre-Deployment Checklist

- [ ] Production database credentials generated and secured
- [ ] TLS certificates acquired and validated
- [ ] API keys and JWT secrets generated
- [ ] Load balancer configuration prepared
- [ ] Monitoring systems configured
- [ ] Backup infrastructure ready
- [ ] Disaster recovery plan reviewed
- [ ] Security audit completed
- [ ] Performance testing passed (>95% verification SLA)
- [ ] Documentation reviewed by ops team

---

## Infrastructure Setup

### AWS Architecture (Recommended)

```
┌─────────────────────────────────────────────────────────┐
│ AWS CloudFront (CDN)                                    │
│ • DDoS protection                                       │
│ • TLS termination                                       │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ AWS ALB (Application Load Balancer)                     │
│ • Health checks                                         │
│ • HTTPS listener (port 443)                             │
│ • Rate limiting                                         │
└────────────┬───────────────────────┬────────────────────┘
             │                       │
    ┌────────▼────────┐    ┌────────▼────────┐
    │ Verification    │    │ Verification    │
    │ Service AZ-1    │    │ Service AZ-2    │
    │ (ECS/Fargate)   │    │ (ECS/Fargate)   │
    └────────┬────────┘    └────────┬────────┘
             │                     │
    ┌────────▼─────────────────────▼─────────┐
    │ RDS Aurora PostgreSQL (Multi-AZ)       │
    │ • Read replicas                        │
    │ • Automated backups                    │
    │ • Encryption at rest                   │
    └────────────────────────────────────────┘
             │
    ┌────────▼─────────────────────────────┐
    │ ElastiCache Redis (Multi-AZ)         │
    │ • Cache layer                        │
    │ • Encryption at rest/transit         │
    └──────────────────────────────────────┘
```

### GCP Architecture (Alternative)

```
┌──────────────────────────────────────────┐
│ Cloud Load Balancer                      │
│ • HTTPS/TLS                              │
│ • Cloud Armor (DDoS protection)          │
└─────────────────┬──────────────────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
    ┌───▼────┐          ┌───▼────┐
    │ GKE    │          │ GKE    │
    │ Nodes: │          │ Nodes: │
    │ 2-5    │          │ 2-5    │
    └───┬────┘          └───┬────┘
        │                   │
    ┌───▼───────────────────▼────┐
    │ Cloud SQL (PostgreSQL)      │
    │ • HA configuration          │
    │ • Automated backups         │
    │ • Replication               │
    └────────────────────────────┘
        │
    ┌───▼────────────────────────┐
    │ Memorystore (Redis)        │
    │ • Cache layer              │
    │ • HA replication           │
    └────────────────────────────┘
```

### Kubernetes Deployment

**Required versions:**
- Kubernetes 1.24+
- Helm 3.10+
- kubectl configured with production cluster

**Namespace setup:**

```bash
# Create dedicated namespace
kubectl create namespace ciaf-prod

# Set default namespace
kubectl config set-context --current --namespace=ciaf-prod

# Create resource quotas
kubectl apply -f - << EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ciaf-quota
  namespace: ciaf-prod
spec:
  hard:
    requests.cpu: "50"
    requests.memory: "100Gi"
    limits.cpu: "100"
    limits.memory: "200Gi"
EOF
```

---

## Security Configuration

### TLS/HTTPS Setup

**Generate certificates:**

```bash
# Option 1: Let's Encrypt (AWS)
aws acm request-certificate \
  --domain-name verify.ciaf.io \
  --validation-method DNS

# Option 2: Self-signed (internal)
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout /etc/ssl/private/ciaf-key.pem \
  -out /etc/ssl/certs/ciaf-cert.pem
```

**Configure in load balancer:**

```bash
# AWS ALB HTTPS listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:... \
  --default-actions Type=forward,TargetGroupArn=arn:aws:...
```

### API Key Management

**Generate production API keys:**

```python
import secrets
import base64

# Generate 32 random bytes = 44 character base64 string
api_key = f"sk_prod_{base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()}"

# Store in AWS Secrets Manager
import boto3
client = boto3.client('secretsmanager')
response = client.create_secret(
    Name='ciaf/prod/api-keys/default',
    SecretString=api_key
)
```

**API Key Scopes (RBAC):**

```python
# Store key policies in database
SCOPES = {
    "sk_prod_analytics": ["read:verify", "read:stats"],
    "sk_prod_compliance": ["read:verify", "read:audit", "read:compliance"],
    "sk_prod_admin": ["read:verify", "read:audit", "read:compliance",
                      "read:stats", "admin:refresh"],
}

# Enforce at runtime
@app.get("/verify/{tag_id}")
async def verify(tag_id: str, api_key: str = Security(get_api_key)):
    user = get_user_from_key(api_key)
    if "read:verify" not in user.scopes:
        raise HTTPException(status_code=403)
    ...
```

### Network Security

**VPC Configuration:**

```hcl
# Terraform: Private subnets only
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1a"
}

# NAT Gateway for outbound internet
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public.id
  depends_on    = [aws_internet_gateway.main]
}
```

**Security Groups:**

```bash
# Verification service (inbound only from ALB)
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxx \
  --protocol tcp --port 8001 \
  --source-security-group-id sg-alb

# PostgreSQL (inbound only from app)
aws ec2 authorize-security-group-ingress \
  --group-id sg-rds \
  --protocol tcp --port 5432 \
  --source-security-group-id sg-app
```

---

## Database Deployment

### PostgreSQL Setup (AWS RDS)

**Create production database:**

```bash
aws rds create-db-instance \
  --db-instance-identifier ciaf-prod-postgres \
  --db-instance-class db.r5.xlarge \
  --engine postgres \
  --engine-version 14.7 \
  --allocated-storage 1000 \
  --storage-type gp3 \
  --iops 3000 \
  --multi-az \
  --backup-retention-period 35 \
  --enable-cloudwatch-logs-exports postgresql \
  --enable-iam-database-authentication \
  --enable-encryption \
  --kms-key-id arn:aws:kms:... \
  --db-subnet-group-name ciaf-prod-db-subnet
```

**Initialize schema:**

```bash
# Connect to production database
PGPASSWORD=$DB_PASSWORD psql \
  -h ciaf-prod-postgres.xxx.us-east-1.rds.amazonaws.com \
  -U ciaf_verification \
  -d ciaf_proofs \
  -f ciaf/verification/POSTGRESQL_SCHEMA.py
```

**Create read replicas:**

```bash
aws rds create-db-instance-read-replica \
  --db-instance-identifier ciaf-prod-postgres-replica-1 \
  --source-db-instance-identifier ciaf-prod-postgres \
  --db-instance-class db.r5.large \
  --availability-zone us-east-1b
```

**Performance Configuration:**

```sql
-- Connect to database and optimize
-- Increase work_memory for complex queries
ALTER SYSTEM SET work_memory = '256MB';

-- Enable query parallelization
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 8;

-- Optimize shared buffers (25% of available RAM)
ALTER SYSTEM SET shared_buffers = '8GB';

-- Connection pool settings
ALTER SYSTEM SET max_connections = 500;

-- Apply changes
SELECT pg_reload_conf();
```

**Connection Pooling (PgBouncer):**

```ini
# /etc/pgbouncer/pgbouncer.ini
[databases]
ciaf_proofs = host=ciaf-prod-postgres.xxx.rds.amazonaws.com \
              port=5432 \
              user=ciaf_verification \
              password=***

[pgbouncer]
pool_mode = transaction
max_client_conn = 5000
default_pool_size = 25
min_pool_size = 10
reserve_pool_size = 5
reserve_pool_timeout = 3
max_db_connections = 100
max_user_connections = 50
server_lifetime = 3600
server_idle_timeout = 600
```

---

## Service Deployment

### Docker Image Build & Push

```bash
# Build image
docker build -t ciaf-verification:1.0.0 .

# Tag for registry
docker tag ciaf-verification:1.0.0 \
  123456789.dkr.ecr.us-east-1.amazonaws.com/ciaf-verification:1.0.0

# Push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/ciaf-verification:1.0.0
```

### Kubernetes Deployment

**Helm Chart (values-prod.yaml):**

```yaml
replicaCount: 3

image:
  repository: 123456789.dkr.ecr.us-east-1.amazonaws.com/ciaf-verification
  tag: "1.0.0"
  pullPolicy: IfNotPresent

resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 1000m
    memory: 1Gi

env:
  DATABASE_URL:
    secretKeyRef:
      name: ciaf-secrets
      key: database-url
  API_KEY_SECRET:
    secretKeyRef:
      name: ciaf-secrets
      key: api-key-secret
  ENVIRONMENT: "production"
  LOG_LEVEL: "WARNING"

service:
  type: ClusterIP
  port: 8001

ingress:
  enabled: true
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: verify.ciaf.io
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: verify-ciaf-tls
      hosts:
        - verify.ciaf.io

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

podDisruptionBudget:
  minAvailable: 2

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
              - key: app
                operator: In
                values:
                  - verification-service
          topologyKey: kubernetes.io/hostname
```

**Deploy:**

```bash
helm upgrade --install ciaf-verification ./helm/ciaf-verification \
  -f values-prod.yaml \
  --namespace ciaf-prod
```

---

## Monitoring & Alerting

### Prometheus Metrics

**Metrics to collect:**

```python
from prometheus_client import Counter, Histogram, Gauge

# Counters
verification_total = Counter(
    'verification_total',
    'Total verification requests',
    ['result']  # success, failed, error
)

# Histograms
verification_duration_seconds = Histogram(
    'verification_duration_seconds',
    'Verification request duration',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

# Gauges
database_connections_active = Gauge(
    'database_connections_active',
    'Active database connections'
)
cache_hit_rate = Gauge(
    'cache_hit_rate',
    'Cache hit rate percentage'
)
```

**Prometheus config:**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

rule_files:
  - 'alerts.yml'

scrape_configs:
  - job_name: 'verification-service'
    static_configs:
      - targets: ['localhost:8001']
    metrics_path: '/metrics'
```

### Alert Rules

**alerts.yml:**

```yaml
groups:
  - name: verification-service
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: |
          rate(verification_total{result="error"}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
          description: "Verification service error rate > 5%"

      # High latency
      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            rate(verification_duration_seconds_bucket[5m])) > 1.0
        for: 10m
        annotations:
          summary: "High verification latency"
          description: "95th percentile latency > 1s"

      # Database unavailable
      - alert: DatabaseDown
        expr: |
          database_connections_active == 0
        for: 2m
        annotations:
          summary: "Database connection lost"

      # Service down
      - alert: ServiceDown
        expr: |
          up{job="verification-service"} == 0
        for: 1m
        annotations:
          summary: "Verification service down"
```

### Alerting Channels

**Configure Alertmanager:**

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/...'

route:
  receiver: 'default'
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h

receivers:
  - name: 'default'
    slack_configs:
      - channel: '#ciaf-alerts'
        title: 'CIAF Verification Alert'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        send_resolved: true

  - name: 'critical'
    pagerduty_configs:
      - service_key: $PAGERDUTY_KEY
        description: '{{ .Alerts | len }} alerts'
```

---

## Backup & Recovery

### PostgreSQL Backups

**Automated backups (AWS RDS):**

```bash
# Set 35-day retention (automatic)
aws rds modify-db-instance \
  --db-instance-identifier ciaf-prod-postgres \
  --backup-retention-period 35 \
  --preferred-backup-window "03:00-04:00" \
  --apply-immediately
```

**Manual backups:**

```bash
# Create snapshot
aws rds create-db-snapshot \
  --db-instance-identifier ciaf-prod-postgres \
  --db-snapshot-identifier ciaf-prod-postgres-backup-$(date +%Y%m%d)

# Export to S3
aws rds start-export-task \
  --export-task-identifier ciaf-export-$(date +%Y%m%d) \
  --source-arn arn:aws:rds:us-east-1:123456789:db:ciaf-prod-postgres \
  --s3-bucket-name ciaf-backups \
  --s3-prefix postgres/ \
  --iam-role-arn arn:aws:iam::123456789:role/rds-s3-export
```

**Point-in-time recovery:**

```bash
# Restore from backup
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier ciaf-prod-postgres-restored \
  --db-snapshot-identifier ciaf-prod-postgres-backup-20250313
```

### Verification Cache Refresh

**After restoring database:**

```python
import asyncio
from ciaf.verification import PostgresProofStore

async def refresh_verification_cache():
    """Refresh all cached merkle proofs."""
    proof_store = PostgresProofStore()
    await proof_store.connect()

    # Clear Redis cache
    cache.flushdb()

    # Rebuild org batch merkle trees
    orgs = await proof_store.get_all_organizations()
    for org_id in orgs:
        windows = await proof_store.get_org_batch_windows(org_id)
        for window in windows:
            cache.set(f"merkle:{window['window_id']}",
                      window['merkle_root'])

    print("Cache refresh complete")

asyncio.run(refresh_verification_cache())
```

---

## Performance Tuning

### Database Query Optimization

```sql
-- Add indexes for common queries
CREATE INDEX CONCURRENTLY idx_verification_lookup ON output_tags(tag_id);
CREATE INDEX CONCURRENTLY idx_org_batch_time ON org_batch_windows(organization_id, window_start DESC);
CREATE INDEX CONCURRENTLY idx_agent_audit ON agent_actions(task_batch_id, timestamp);

-- Analyze tables
ANALYZE output_tags;
ANALYZE task_batches;
ANALYZE org_batch_windows;
ANALYZE agent_actions;

-- Check slow queries
SELECT query, calls, total_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

### Connection Pool Tuning

**Optimal pool size formula:**

```
pool_size = (
  (number_of_app_instances * app_connections_per_instance) +
  (number_of_backup_pools * 5)
)

For: 5 pods × 20 connections each
pool_size = (5 × 20) + (2 × 5) = 110
```

**Apply to RDS:**

```bash
aws rds modify-db-parameter-group \
  --db-parameter-group-name ciaf-prod-params \
  --parameters \
    ParameterName=max_connections,ParameterValue=500,ApplyMethod=immediate \
    ParameterName=shared_buffers,ParameterValue=262144,ApplyMethod=pending
```

### Caching Strategy

**Redis cache configuration:**

```python
# Cache policy: LRU (least recently used)
# Max memory: 2GB
# Eviction when full: Remove LRU items

cache_config = {
    'host': 'ciaf-redis.xxxx.ng.0001.use1.cache.amazonaws.com',
    'port': 6379,
    'db': 0,
    'socket_connect_timeout': 5,
    'socket_timeout': 5,
    'connection_pool_kwargs': {
        'max_connections': 100,
        'retry_on_timeout': True,
    }
}

# TTLs
CACHE_TTLS = {
    'output_tag': 300,          # 5 minutes
    'merkle_proof': 3600,       # 1 hour (org windows immutable)
    'org_stats': 3600,          # 1 hour
    'compliance_report': 1800   # 30 minutes
}
```

---

## Troubleshooting

### Service Not Responding

```bash
# Check service health
curl -v https://verify.ciaf.io/health

# Check pod logs
kubectl logs -n ciaf-prod deployment/ciaf-verification --tail=100

# Check resource usage
kubectl describe pod -n ciaf-prod $(kubectl get pods -n ciaf-prod -o name | head -1)

# Check database connection
kubectl exec -n ciaf-prod [pod-name] -- \
  psql -h $DB_HOST -U ciaf_verification -d ciaf_proofs -c "SELECT 1"
```

### High Error Rate

```bash
# Check recent errors
kubectl logs -n ciaf-prod deployment/ciaf-verification --since=10m | grep ERROR

# Check database performance
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value=ciaf-prod-postgres \
  --start-time 2025-03-13T14:00:00Z \
  --end-time 2025-03-13T15:00:00Z \
  --period 300 \
  --statistics Average,Maximum
```

### Database Timeout

```bash
# Check connection pool
curl http://localhost:8001/metrics | grep 'pool'

# Increase pool size dynamically
kubectl set env -n ciaf-prod deployment/ciaf-verification \
  POOL_SIZE=50 MAX_OVERFLOW=20

# Monitor connections
watch -n 5 "aws rds describe-db-instances --db-instance-identifier ciaf-prod-postgres \
  --query 'DBInstances[0].DBParameterGroups[0].{DBInstanceIdentifier,Status}'"
```

---

## Incident Response

### Critical Outage Response Plan

**Severity 1 (Total Down):**

1. **Alert Team (0-5 min)**
   - Page on-call engineer
   - Notify engineering lead
   - Update status page: "Investigating"

2. **Assess & Mitigate (5-15 min)**
   ```bash
   # Check service status
   kubectl get pods -n ciaf-prod
   kubectl top nodes

   # Check database
   aws rds describe-db-instances --db-instance-identifier ciaf-prod-postgres

   # Check logs
   kubectl logs -n ciaf-prod -l app=verification-service --tail=500 | tail -50
   ```

3. **Recover (15-45 min)**
   - Restart service: `kubectl rollout restart deployment/ciaf-verification -n ciaf-prod`
   - Rebuild cache: `POST /admin/refresh-cache`
   - Verify: `curl https://verify.ciaf.io/health`

4. **Post-Incident (Next day)**
   - Root cause analysis
   - Update runbook
   - Deploy fix

**Severity 2 (Degraded):**

1. Scale up replicas
2. Monitor error rate
3. Document in incident log

### Rollback Procedure

```bash
# Get previous deployment
kubectl rollout history deployment/ciaf-verification -n ciaf-prod

# Rollback to previous version
kubectl rollout undo deployment/ciaf-verification \
  --to-revision=5 \
  -n ciaf-prod

# Verify
kubectl rollout status deployment/ciaf-verification -n ciaf-prod
```

---

## Compliance & Security

### SOC 2 Type II Requirements

- ✅ Encryption at rest (AWS KMS)
- ✅ Encryption in transit (TLS 1.3)
- ✅ Access control (RBAC with scopes)
- ✅ Audit logging (CloudTrail)
- ✅ Change control (immutable backups)
- ✅ Incident response plan (documented above)

### HIPAA Compliance (if required)

```bash
# Enable HIPAA logging
aws rds modify-db-instance \
  --db-instance-identifier ciaf-prod-postgres \
  --enable-iamdatabase-authentication \
  --enable-cloudwatch-logs-exports postgresql
```

### GDPR Data Deletion

```sql
-- Right to be forgotten (delete user data after 90 days of inactivity)
DELETE FROM agent_sessions
WHERE ended_at < NOW() - INTERVAL '90 days';

-- Cascade delete tags and actions
DELETE FROM output_tags
WHERE session_id NOT IN (SELECT session_id FROM agent_sessions);
```

---

## Support & Escalation

**On-Call Engineer:**
- PagerDuty: CIAF Verification Service
- Slack: #ciaf-incidents-prod

**Escalation Matrix:**
- Level 1: Service Engineer (3am-11pm)
- Level 2: Platform Team Lead (24/7)
- Level 3: VP Engineering (critical only)

**Runbook Updates:**
- After each incident: Update this document
- Every 6 months: Full review
- Before major changes: Test procedures

---

Created: 2025-03-13
Last Updated: 2025-03-13
Version: 1.0.0
License: BUSL-1.1 (converts to Apache 2.0 on Jan 1, 2029)
