# Industry Frameworks & Policy Mapping

How to map CIAF policies to specific regulatory obligations and demonstrate compliance.

## Overview

CIAF contains **1,847 policy IDs** across **20 industries**, each mapped to specific regulatory requirements.

This guide shows you how to:
1. Find the policy ID for your regulation
2. Understand what it requires
3. Implement it in your AI system
4. Verify compliance during audit

---

## Quick Lookup: Regulation → Policy ID

### Healthcare (HIPAA)

| Regulation | CIAF Policy IDs | What It Requires |
|-----------|-----------------|-----------------|
| **164.312(a)(2)(i)** - Access Controls | HIPAA-001, HIPAA-002 | Authenticate users, log access |
| **164.312(b)** - Audit & Accountability | HIPAA-010 → HIPAA-020 | Maintain immutable audit logs |
| **164.308(a)(3)(ii)(C)** - Workforce Security | HIPAA-030 → HIPAA-040 | Role-based access, termination procedures |
| **164.308(a)(4)** - Needs Assessment | HIPAA-050 → HIPAA-060 | Document security requirements |
| **164.514(b)** - De-identification | HIPAA-070 → HIPAA-080 | Remove PHI before ML training |

### Financial Services (Gramm-Leach-Bliley Act)

| Regulation | CIAF Policy IDs | What It Requires |
|-----------|-----------------|-----------------|
| **12 CFR 30, Appendix B** - Safeguards Rule | GLBA-001 → GLBA-050 | Comprehensive security program |
| **15 USC 6801** - Privacy Rule | GLBA-060 → GLBA-080 | Privacy notices, customer choice |
| **12 CFR 748** - Breach Notification | GLBA-090 → GLBA-100 | Notify customers of data breaches |

### EU (GDPR)

| Regulation | CIAF Policy IDs | What It Requires |
|-----------|-----------------|-----------------|
| **Article 5** - Data Protection Principles | GDPR-001 → GDPR-010 | Lawfulness, fairness, transparency |
| **Article 32** - Security of Processing | GDPR-020 → GDPR-040 | Encryption, pseudonymization |
| **Article 33-34** - Breach Notification | GDPR-050 → GDPR-060 | Notify DPA within 72 hours |
| **Article 22** - Automated Decision-Making | GDPR-070 → GDPR-090 | Right to explanation, human review |

### US Federal (NIST AI RMF)

| Requirement | CIAF Policy IDs | What It Requires |
|------------|-----------------|-----------------|
| **GOVERN** - Establish policies | NIST-001 → NIST-050 | AI governance framework |
| **MAP** - Identify risks | NIST-060 → NIST-100 | Risk assessment, documentation |
| **MEASURE** - Monitor performance | NIST-110 → NIST-150 | Continuous monitoring |
| **MANAGE** - Handle risks | NIST-160 → NIST-200 | Mitigation, response procedures |

---

## Deep Dive: HIPAA Compliance Example

### Requirement: HIPAA 164.308(a)(3)(ii)(C) - Workforce Security

**What the regulation says:**
"Implement policies and procedures to ensure that all members of its workforce have been appropriately authorized."

**What it means:**
- Only authorized people can access patient data
- Each person's access is documented
- Access is removed when they leave
- There's an audit trail

### CIAF Implementation: HIPAA-030 → HIPAA-040

```json
{
  "policy_id": "HIPAA-030",
  "policy_name": "Access Control Policy",
  "requirement": "164.308(a)(3)(ii)(C)",
  "description": "Implement user authentication and authorization for all data access",

  "controls": [
    {
      "control_id": "HIPAA-030-001",
      "name": "Multi-factor Authentication",
      "requirement": "All users must authenticate with 2+ factors",
      "implementation": {
        "tool": "auth_service",
        "config": {
          "mfa_required": true,
          "allowed_factors": ["password", "totp", "hardware_key"],
          "session_timeout": 3600
        }
      }
    },
    {
      "control_id": "HIPAA-030-002",
      "name": "Role-Based Access Control (RBAC)",
      "requirement": "Users can only access data for their role",
      "implementation": {
        "tool": "rbac_engine",
        "roles": [
          {
            "role": "physician",
            "permissions": ["read:patient_records", "write:diagnoses"]
          },
          {
            "role": "nurse",
            "permissions": ["read:patient_records", "write:vitals"]
          },
          {
            "role": "billing",
            "permissions": ["read:patient_billing", "write:invoices"]
          }
        ]
      }
    },
    {
      "control_id": "HIPAA-030-003",
      "name": "Access Audit Logging",
      "requirement": "Every access to patient data is logged (who, what, when, from where)",
      "implementation": {
        "tool": "audit_service",
        "log_events": [
          {"event": "login", "fields": ["user_id", "timestamp", "ip_address"]},
          {"event": "data_access", "fields": ["user_id", "patient_id", "data_type", "action"]},
          {"event": "logout", "fields": ["user_id", "timestamp", "session_duration"]}
        ],
        "retention": "7_years",
        "worm_protected": true
      }
    }
  ]
}
```

### Verification Process

**During Audit, Healthcare Auditor Checks:**

1. **Authentication Proof**
   ```bash
   # Verify MFA is enabled
   curl -X POST http://localhost:8000/v1/auth/verify \
     -d '{"user": "dr_smith", "check": "mfa_enforced"}'
   # Response: { "mfa_required": true, "factors": ["password", "totp"] }
   ```

2. **RBAC Configuration**
   ```bash
   # List roles
   curl -X GET http://localhost:8000/v1/rbac/roles \
     -d '{"org": "healthcare-org-1"}'
   # Response: [ { "role": "physician", "permissions": [...] } ]
   ```

3. **Audit Logs**
   ```bash
   # Query access logs for specific patient
   curl -X GET http://localhost:8000/v1/audit/logs \
     -d '{
       "patient_id": "P-2026-001",
       "from_date": "2025-01-01",
       "to_date": "2026-12-31"
     }'
   # Response: [ { "user": "dr_smith", "action": "read_record", "timestamp": "..." } ]
   ```

4. **Termination Verification**
   ```bash
   # Verify access removed when employee left
   curl -X GET http://localhost:8000/v1/rbac/access_history \
     -d '{"user": "former_nurse_jones"}'
   # Response: { "access_revoked": true, "revoked_at": "2025-06-30" }
   ```

### Compliance Documentation

**Auditor generates compliance report:**

```markdown
# HIPAA 164.308(a)(3)(ii)(C) Compliance Report

## Requirement: Workforce Security & Access Control

✅ **COMPLIANT**

### Findings:

1. **Multi-Factor Authentication**
   - Status: ✅ Enforced for all users
   - Evidence: System verified MFA required for all logins
   - Audit Period: Verified 100% of logins (2,345 logins) used MFA

2. **Role-Based Access Control**
   - Status: ✅ Configured correctly
   - Evidence: 8 roles defined with appropriate permissions
   - Audit Period: No unauthorized access attempts detected

3. **Access Audit Logging**
   - Status: ✅ Complete audit trail maintained
   - Coverage: 100% of data access events logged
   - Retention: 7 years (exceeds HIPAA requirement)
   - Integrity: WORM-protected, immutable

4. **Access Termination**
   - Status: ✅ Timely revocation implemented
   - Process: Average revocation time: 2 hours
   - Recent Example: Nurse Jones (ID: N-2025-847) access revoked 2025-06-30

### Conclusion:

The organization has **fully implemented** the HIPAA 164.308(a)(3)(ii)(C)
workforce security requirement. Access controls are enforced, auditable,
and appropriately documented.
```

---

## Policy Lookup by Organization Type

### You Are: Healthcare Provider

**Start here:**

1. **Primary:** HIPAA policies (HIPAA-001 → HIPAA-200)
   - Focus on: Patient access, audit trails, data security

2. **Secondary:** NIST AI RMF (NIST-060 → NIST-100)
   - Focus on: AI risk assessment, model monitoring

3. **Optional:** State-specific (CA-001 → CA-050)
   - If operating in California

**Typical implementation time:** 6-8 weeks
**Policies to implement:** ~35
**Estimated cost:** $50K-100K

### You Are: Financial Institution

**Start here:**

1. **Primary:** GLBA policies (GLBA-001 → GLBA-150)
   - Focus on: Information security, privacy, breach notification

2. **Secondary:** SOX policies (SOX-001 → SOX-080)
   - If public company, focus on: Internal controls, audit trails

3. **Tertiary:** NIST AI RMF (NIST-001 → NIST-200)
   - Focus on: Algorithmic trading, credit decision AI

**Typical implementation time:** 8-12 weeks
**Policies to implement:** ~45
**Estimated cost:** $100K-200K

### You Are: Tech Company Operating in EU

**Start here:**

1. **Primary:** GDPR policies (GDPR-001 → GDPR-150)
   - Focus on: Data rights, automated decisions, breach notification

2. **Secondary:** EU AI Act (EU-AI-001 → EU-AI-100)
   - Focus on: High-risk AI classification, transparency requirements

3. **Tertiary:** NIST AI RMF (NIST-001 → NIST-200)
   - Focus on: Internal governance, risk management

**Typical implementation time:** 10-16 weeks (complex!)
**Policies to implement:** ~60
**Estimated cost:** $150K-300K

---

## Custom Policy Creation

### For Your Specific Use Case

If your AI system isn't covered by industry frameworks, create custom policies:

```json
{
  "organization_id": "custom-org-1",
  "policy_id": "CUSTOM-ML-001",
  "policy_name": "Custom Machine Learning Training Policy",
  "description": "Our organization uses ML for X. This policy ensures Y.",

  "controls": [
    {
      "control_id": "CUSTOM-ML-001-001",
      "name": "Data Quality Assurance",
      "requirement": "All training data must pass quality checks",
      "implementation": {
        "checks": [
          "no_duplicates",
          "no_extreme_outliers",
          "class_balance_verified",
          "manual_spot_check_10_percent"
        ],
        "responsibility": "Data Engineer",
        "frequency": "Every training run"
      }
    },
    {
      "control_id": "CUSTOM-ML-001-002",
      "name": "Bias Testing",
      "requirement": "Model must pass fairness tests across demographic groups",
      "implementation": {
        "tests": [
          "demographic_parity",
          "equal_opportunity",
          "calibration",
          "disparate_impact"
        ],
        "threshold": "pass_all_tests",
        "responsibility": "Data Scientist",
        "frequency": "Before production deployment"
      }
    }
  ]
}
```

---

## Compliance Dashboard

Monitor your policy implementation in real-time:

```
┌─────────────────────────────────────────────┐
│ HEALTHCARE-ORG-1 COMPLIANCE DASHBOARD       │
├─────────────────────────────────────────────┤
│                                             │
│ HIPAA Compliance        ████████████ 95%   │
│ ├─ Access Controls      ████████████ 100%  │
│ ├─ Audit Trails         ████████████ 100%  │
│ ├─ Data Encryption      ████████░░░░ 80%   │
│ ├─ Breach Notification  ████████████ 100%  │
│ └─ Employee Training    ████████░░░░ 85%   │
│                                             │
│ NIST AI RMF             ████████░░░░ 75%   │
│ ├─ GOVERN               ████████████ 100%  │
│ ├─ MAP                  ████████░░░░ 85%   │
│ ├─ MEASURE              ███████░░░░░ 70%   │
│ └─ MANAGE               ███████░░░░░ 65%   │
│                                             │
│ ⚠️  ACTION ITEMS:                           │
│ • Encryption: Upgrade TLS 1.1 → 1.2 (2h)   │
│ • Monitoring: Add dashboard for MEASURE     │
│ • Training: Schedule Q1 compliance training │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Audit-Ready Checklist

Before your audit, verify:

| Item | Status | Action |
|------|--------|--------|
| [ ] All 1,847 policies reviewed | N/A | Identify which apply to your organization |
| [ ] Applicable policies identified | N/A | Typically 30-60 policies apply |
| [ ] Controls implemented | N/A | Code, process, or documentation |
| [ ] Cryptographic proofs generated | ✅ | CIAF handles this automatically |
| [ ] Audit logs maintained | ✅ | WORM-protected for 7 years default |
| [ ] Evidence organized | N/A | Create audit binders per policy |
| [ ] Auditor briefing prepared | N/A | 1-2 hour walkthrough recommended |
| [ ] Expert witnesses identified | N/A | For complex technical policies |

---

## Next Steps

- [Quick Start](../01-quickstart/5min-compliance-flow.md) - Implement your first policy
- [Observability Guide](../04-observability/dashboard-guide.md) - Monitor compliance in real-time
- [Auditor's View](../05-auditors-view/manual-verification.md) - Prepare for audit
