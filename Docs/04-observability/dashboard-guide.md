# Observability & SRE Guide

Understand and act on CIAF monitoring dashboards and alert rules.

## Overview

CIAF includes **22 alert rules** and **3 production dashboards** for monitoring system health, security, and performance.

This guide teaches you:
1. **What each metric means**
2. **How to interpret alerts**
3. **What to do when alerts fire**
4. **How to tune thresholds**

---

## Dashboard 1: System Health

**URL:** http://localhost:3001 → System Health Dashboard

Shows the baseline health of CIAF services.

### Panel 1: API Latency (p95)

**What it measures:** The 95th percentile of request latency (95% of requests finish faster than this)

```
Red   (>1000ms): ❌ Critical - Users experiencing delays
Yellow (500-1000ms): ⚠️ Warning - Getting close to timeout
Green (<500ms): ✅ Healthy - Users won't notice latency
```

**If HIGH:**
- Check database connection pool (`SELECT COUNT(*) FROM pg_stat_activity`)
- Check CPU usage (`top`)
- Run EXPLAIN ANALYZE on slow queries
- Consider caching results

**If SPIKING:**
- Someone doing a big export/query
- Database under heavy load
- Network connectivity issue

### Panel 2: Request Rate

**What it measures:** Requests per second (throughput)

```
Normal pattern: Steady during business hours, drops at night
Spike: Double+ the normal rate
Sustained increase: Traffic growth or traffic loop
```

**If SPIKING:**
- This might be normal (users on system)
- OR someone is doing a bulk operation
- OR there's a runaway request loop (check logs)

**Action:** If coupled with high latency, likely a performance issue

### Panel 3: Error Rate

**What it measures:** Percentage of requests returning 5xx errors

```
Red   (>5%):    ❌ Critical - Many requests failing
Yellow (1-5%):  ⚠️ Warning - More errors than normal
Green (<1%):    ✅ Healthy
```

**If HIGH:**
- Check application logs for error patterns
- Verify database connectivity
- Check downstream services (Vault, external APIs)

### Panel 4: Database Connections

**What it measures:** Active database connections vs. pool limit

```
Green:  <50% of pool (plenty of headroom)
Yellow: 50-80% of pool (getting tight, watch for spikes)
Red:    >80% of pool (risk of connection pool exhaustion)
```

**If RISING:**
- Requests are slow (connections held longer)
- Someone opened a long-running transaction
- Bug in connection pooling

**Fix:**
```sql
-- Kill long-running queries
SELECT pid FROM pg_stat_activity
WHERE state = 'active' AND query_start < NOW() - INTERVAL '10 minutes';

-- Restart application process to reset pool
docker-compose restart verification-service
```

### Panel 5: Proof Generation & Verification Rate

**What it measures:** Proofs generated and verified per second

```
Normal: Steady baseline (maybe 1-10 proofs/sec during normal ops)
Spikes: Auditor requesting proof batch materialization (10-100 proofs/sec)
Zero: No proof activity (normal if no recent inferences)
```

**If HIGH AND SUSTAINED:**
- Normal during audit/proof generation window
- Monitor to completion
- Customer is generating a lot of proofs

**If ZERO FOR DAYS:**
- Either your system isn't recording inferences
- OR proofs are cached and not being regenerated
- Check that AI system is still running

### Panel 6: Cache Hit Rate

**What it measures:** What percentage of data comes from cache vs. database

```
Green:  >80% (most reads from cache)
Yellow: 50-80% (cache working but could be better)
Red:    <50% (cache not effective, queries hitting database)
```

**If LOW:**
- Cache hasn't warmed up yet (normal at startup)
- Cache key strategy is wrong
- Database changed, invalidating cache
- Consider increasing cache size

---

## Dashboard 2: Security

**URL:** http://localhost:3001 → Security Dashboard

Detects security incidents and anomalies.

### Panel 1: Failed Authentication Attempts

**What it measures:** Login failures per time period

```
Red   (>20/hour): ❌ Likely brute force attack
Yellow (10-20/hour): ⚠️ Elevated - might be users with wrong passwords
Green (<10/hour): ✅ Normal - few failed logins
```

**If SPIKING:**
- Check logs for repeated IPs (`SELECT ip_address, COUNT(*) FROM auth_failures GROUP BY ip_address`)
- If same IP: Likely brute force, consider IP banning
- If many IPs: Could be credential leak, force password reset

**Automated Response:**
- After 10 failed attempts in 5 minutes → IP block for 15 minutes
- After 30 failed attempts in 1 hour → Force CAPTCHA for that IP

### Panel 2: Rate Limit Violations

**What it measures:** Requests exceeding rate limits

```
Red   (>5/min): ❌ System under DoS attack
Yellow (1-5/min): ⚠️ Someone (or auto-script) hammering API
Green (0):        ✅ All requests within limits
```

**If SPIKING:**
- Legitimate: Bulk export, data sync, scheduled task
- Malicious: Someone trying to break in, DoS attack
- Buggy: Your own application in a loop

**Check rate limit config:**
```bash
# Default: 100 requests per minute
# Increase if you have legitimate heavy usage:
RATE_LIMIT_REQUESTS_PER_MINUTE=500

# Per-IP limit:
RATE_LIMIT_PER_IP_MINUTE=100
```

### Panel 3: Proof Tampering Detection

**What it measures:** Signatures failing verification (attempted tampering)

```
Red   (>0): ❌ CRITICAL - Tampering detected!
Green (0):  ✅ No tampering - proofs are authentic
```

**If ANY ALERTS:**
- This is a security incident
- All tampered proofs identified automatically
- Evidence preserved in immutable audit logs
- **IMMEDIATE ACTION:** Notify security team, preserve evidence

### Panel 4: Cryptographic Verification Failures

**What it measures:** Proofs that fail cryptographic verification

**Typical causes:**
- ✅ Normal: Malformed proof uploaded by mistake (retried with valid proof)
- ❌ Serious: Systematic failures (possible configuration issue)
- ❌ Critical: Hash/signature failures (tampering)

**If ELEVATED:**
- Check if certain batch is repeatedly failing
- Verify public key is correct
- Run manual verification on sample proof

---

## Dashboard 3: Performance

**URL:** http://localhost:3001 → Performance Dashboard

Deep performance metrics for optimization.

### Panel 1: Database Query Latencies (p95, p99)

**What it measures:** How long database queries take

```
p95: 95% of queries finish within this time
p99: 99% of queries finish within this time (accounts for outliers)

Green:  p95<50ms, p99<100ms  ✅
Yellow: p95<100ms, p99<200ms ⚠️
Red:    p95>100ms, p99>200ms ❌
```

**If HIGH:**
- Check for missing indexes
- Run ANALYZE on tables
- Check for full table scans: `EXPLAIN ANALYZE SELECT ...`
- Consider caching results

**Example slow query:**
```sql
-- SLOW (full table scan):
SELECT COUNT(*) FROM output_tags WHERE organization_id = 'healthcare-org-1';

-- FAST (uses index):
SELECT COUNT(*) FROM output_tags WHERE organization_id = 'healthcare-org-1' AND created_at > NOW() - INTERVAL '30 days';
```

### Panel 2: Active Database Connections

**What it measures:** Connections currently in use

```
Green: <20 connections (healthy)
Yellow: 20-40 connections (monitor)
Red: >40 connections (saturated)
```

**If CONSTANTLY HIGH:**
- Application is making too many parallel requests
- Connections aren't being returned to pool
- Database is slow (connections held longer)

**Fix:**
```python
# ciaf/verification/api.py
# Reduce from default:
pool = create_async_engine(
    DATABASE_URL,
    pool_size=50,        # ← Was high
    max_overflow=20,
).update to:
    pool_size=20,        # ← More conservative
    max_overflow=5,
```

### Panel 3: Throughput

**What it measures:** Successful queries + proof operations per second

```
Query Ops: SELECT, UPDATE, INSERT queries per second
Proof Ops: Hash computations, tree materializations per second
```

**Expected patterns:**
- Morning spike (users come online)
- Lunchtime dip (people on break)
- Evening spike (catch-up work)
- Night low (automated tasks only)

**If ZERO:**
- Database might be unreachable
- All requests failing (check error rate on system health)

---

## Alert Rules: What to Do

### System Alerts (10 rules)

| Alert | When | Severity | Action |
|-------|------|----------|--------|
| **High API Latency** | p95 > 1000ms | P2 | Check database, restart service if needed |
| **High Error Rate** | Error % > 5% | P2 | Check logs, page oncall engineer |
| **Connection Pool Exhaustion** | >90% utilized | P2 | Investigate slow queries, increase pool |
| **Database Down** | Ping fails | P1 | Page DBA, check RDS console |
| **Memory Leak** | Growing memory without reset | P3 | Restart service, investigate memory profirle |
| **Disk Space Low** | <10% free | P2 | Archive old logs, expand filesystem |
| **CPU Spike** | >90% for 5 min | P2 | Check for runaway query, restart if needed |
| **OOM Killer Active** | Process killed by kernel | P1 | Increase instance RAM, restart service |
| **Prometheus Scrape Failure** | Can't scrape metrics | P3 | Check service health, verify network |
| **Clock Skew Detected** | System time difference >1s | P3 | Check NTP sync on server |

### Security Alerts (12 rules)

| Alert | When | Severity | Action |
|-------|------|----------|--------|
| **Brute Force Attempt** | >10 failed logins/5min from IP | P1 | Auto-block IP, notify security |
| **Credential Stuffing** | >30 failed logins/hour from subnet | P1 | Block subnet, notify IR team |
| **Unauthorized API Access** | Invalid token used >5 times | P2 | Revoke tokens, audit user |
| **Rate Limit Exceeded** | >5 times in 1 min from IP | P2 | Block IP (15 min), log for investigation |
| **Proof Tampering Detected** | Signature verification fails | P1 | PAGE IMMEDIATELY, preserve evidence |
| **Audit Log Truncation** | INSERT-only log has deletes | P1 | PAGE IMMEDIATELY, investigate loss |
| **Unauthorized Database Access** | Query from unknown user | P1 | Kill connection, audit access logs |
| **SSL/TLS Certificate Expired** | Cert expiry < 30 days | P2 | Renew certificate, monitor renewal |
| **API Key Rotation Overdue** | Key in use >365 days | P2 | Schedule key rotation immediately |
| **Suspicious Vaulting Activity** | >1000 proofs submitted/hour | P2 | Verify not an audit in progress, investigate |
| **Public Key Mismatch** | Public key changed unexpectedly | P1 | PageImmediately, verify change legitimacy |
| **Anomalous Data Access Pattern** | User accessing unusual data | P3 | Investigate user activity, possible breach |

### Response Runbooks

#### When You See: "Proof Tampering Detected"

```
SEVERITY: P1 - CRITICAL SECURITY INCIDENT
RESPONSE TIME: Immediate (page oncall, no auto-responder waits)

Step 1: Verify Alert Is Real
  ✓ Check Grafana dashboard manually
  ✓ Verify tampering in audit logs
  ✓ Don't assume false positive

Step 2: Preserve Evidence
  ✓ DO NOT clear logs or restart services
  ✓ Take filesystem snapshots
  ✓ Export all audit logs to secure storage
  ✓ Notify legal team

Step 3: Investigate
  ✓ Which proofs were tampered with?
  ✓ When did tampering occur?
  ✓ Who had access to the system?
  ✓ Was it a sophisticated attack or misconfiguration?

Step 4: Communicate
  ✓ Notify CEO/board immediately
  ✓ Brief legal team
  ✓ Prepare breach notification if data was accessed
  ✓ Brief regulators per compliance requirements

Step 5: Analysis
  ✓ Did attacker modify proof data?
  ✓ OR did they just make invalid signatures?
  ✓ If data was legitimate, proof of tampering = good defense
  ✓ If data was changed, this is a data breach
```

#### When You See: "High Error Rate"

```
SEVERITY: P2 - Service Degradation
RESPONSE TIME: <5 minutes

Step 1: Assess Impact
  ✓ Check error rate percentage
  ✓ Is it 5% (some users affected) or 50% (melting down)?
  ✓ How many users impacted?

Step 2: Identify Root Cause (30 sec)
  ✓ Check database connectivity (ping, reachability)
  ✓ Check application services status (docker ps)
  ✓ Check disk space and memory

Step 3: Quick Fixes (in priority order)
  a) Database unreachable? Restart database connection
  b) Service crashed? Restart service
  c) Out of memory? Restart service + check for memory leak
  d) Out of disk? Clear logs, expand PV

Step 4: Monitor Recovery
  ✓ Watch error rate for 5 minutes
  ✓ Verify error rate returns to <1%
  ✓ If not fixed, escalate to on-call engineer

Step 5: Post-Incident
  ✓ Review error logs for root cause
  ✓ Create ticket to fix underlying issue
  ✓ Add monitoring for this pattern
```

---

## Tuning Alert Thresholds

### Default Thresholds

```yaml
# monitoring/alerts/system.yaml

- alert: HighAPILatency
  expr: histogram_quantile(0.95, http_request_duration_seconds) > 1.0
  # ↑ Fires if p95 latency is over 1 second

- alert: HighErrorRate
  expr: (sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) > 0.05
  # ↑ Fires if error rate over 5%

- alert: ConnectionPoolExhaustion
  expr: (pg_connections_active / pg_stat_activity.setting.max_connections) > 0.9
  # ↑ Fires if 90% of connections in use
```

### Tuning for Your System

**If getting false alarms:**

```yaml
# healthcare-org-1 uses bursty traffic (appointments at opening)
# Lower threshold during burst hour, higher otherwise

- alert: HighAPILatency
  expr: histogram_quantile(0.95, http_request_duration_seconds) > 1.0
  for: 5m  # ← Only fire if sustained for 5 minutes
  # Prevents single spike from alerting

- alert: HighErrorRate
  expr: (error_rate > 0.05) AND (error_rate > (baseline_error_rate * 2))
  # ← Only alert if error rate doubled from baseline
  # More intelligent than hardcoded threshold
```

**Baseline metrics (collect for 1 week):**

```bash
# Safe defaults after 1 week of data:
- API Latency p95: 95th percentile of your environment
- Error Rate: Baseline + 50%
- Connection Pool: 80% of your typical peak
```

---

## Custom Dashboards

Create org-specific dashboards:

```json
{
  "dashboard": "healthcare-org-1-sla",
  "title": "Healthcare Org SLA Metrics",
  "panels": [
    {
      "title": "Uptime %",
      "metric": "(total_requests - failed_requests) / total_requests * 100",
      "target_sla": "99.9%"
    },
    {
      "title": "P50/P95/P99 Latencies",
      "metrics": [
        "histogram_quantile(0.50, ...)",
        "histogram_quantile(0.95, ...)",
        "histogram_quantile(0.99, ...)"
      ]
    },
    {
      "title": "HIPAA Audit Log Completion",
      "metric": "audit_log_completeness_percent",
      "target": "100%"
    }
  ]
}
```

---

## Next Steps

- [System Health Dashboard](http://localhost:3001) - See metrics in real-time
- [Alert Configuration](../monitoring/alerts/system.yaml) - Tune thresholds
- [Industry Frameworks](../03-industry-frameworks/policy-mapping-guide.md) - Compliance monitoring
