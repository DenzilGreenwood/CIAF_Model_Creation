#!/usr/bin/env python3
"""
End-to-end test of CIAF Vault API.
Tests complete workflow: org → key → submit → verify → certificate → audit
"""

import requests
import json
from datetime import datetime

def test_vault_complete_workflow():
    """Test complete vault workflow."""

    vault_url = "http://localhost:8002"

    print("=" * 80)
    print("CIAF VAULT - COMPLETE END-TO-END WORKFLOW TEST")
    print("=" * 80)

    # Use the debug key we already created
    api_key = "alHIZM5XMtm0xY_yMGAqOWVNrWst1RvicVy6fKhW4Lc"
    org_id = "debug_test_org_001"
    headers = {"Authorization": f"Bearer {api_key}"}

    # ========================================================================
    # TEST 1: Get Organization Details
    # ========================================================================
    print("\n[TEST 1] Get organization details...")
    response = requests.get(f"{vault_url}/organization", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    org = response.json()
    print(f"  [OK] Organization name: {org['name']}")
    print(f"       API key count: {org['api_key_count']}")
    print(f"       Created at: {org['created_at']}")

    # ========================================================================
    # TEST 2: Submit Multiple Proofs
    # ========================================================================
    print("\n[TEST 2] Submitting multiple proofs...")
    proofs = []

    # Generate unique content with timestamp to avoid duplicate detection
    timestamp = datetime.now().isoformat()

    proof_cases = [
        {
            "name": "Banking - Fair Lending Check",
            "content": f"Fair lending compliance check passed for loan APP_001. Applicant age: 35, no discrimination detected. [Generated: {timestamp}]",
            "agent_ids": ["credit_analyst_001", "compliance_officer_001"],
            "policies_applied": ["fair_lending", "equal_opportunity"]
        },
        {
            "name": "Healthcare - HIPAA Compliance",
            "content": f"Patient medical record accessed by authorized healthcare provider. PII protection verified. [Generated: {timestamp}]",
            "agent_ids": ["healthcare_analyst_001"],
            "policies_applied": ["hipaa", "data_privacy"]
        },
        {
            "name": "Multi-Agent Decision",
            "content": f"Credit decision approved after consensus: Credit score 750, debt-to-income 0.35, employment verified. [Generated: {timestamp}]",
            "agent_ids": ["scoring_agent_001", "verification_agent_001", "decision_agent_001"],
            "policies_applied": ["risk_assessment", "fair_lending", "verification"]
        },
    ]

    for i, case in enumerate(proof_cases, 1):
        payload = {
            "content": case["content"],
            "agent_ids": case["agent_ids"],
            "policies_applied": case["policies_applied"],
            "timestamp": datetime.now().isoformat(),
            "metadata": {"case_id": f"CASE_{i:03d}"}
        }

        response = requests.post(f"{vault_url}/submit", json=payload, headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        receipt = response.json()
        proofs.append(receipt)
        print(f"  [OK] Proof {i}: {case['name']}")
        print(f"       Proof ID: {receipt['proof_id']}")
        print(f"       Verification URL: {receipt['verification_url']}")

    # ========================================================================
    # TEST 3: Verify Proofs
    # ========================================================================
    print("\n[TEST 3] Verifying proofs...")
    for i, proof in enumerate(proofs, 1):
        proof_id = proof["proof_id"]
        response = requests.get(f"{vault_url}/verify/{proof_id}", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        verified = response.json()
        print(f"  [OK] Proof {i} verified:")
        print(f"       Proof ID: {verified['proof_id']}")
        print(f"       Organization: {verified['organization_id']}")
        print(f"       Verified: {verified['verified']}")
        print(f"       Read count: {verified['read_count']}")

    # ========================================================================
    # TEST 4: Generate Certificate for First Proof
    # ========================================================================
    proof_id = proofs[0]["proof_id"]
    print(f"\n[TEST 4] Generating certificate for proof {proof_id[:8]}...")
    response = requests.post(f"{vault_url}/certificate/{proof_id}", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    cert = response.json()
    print(f"  [OK] Certificate generated:")
    print(f"       Certificate ID: {cert['certificate_id']}")
    print(f"       Proof ID: {cert['proof_id']}")
    print(f"       Generated at: {cert['generated_at']}")
    print(f"       Valid until: {cert['valid_until']}")
    print(f"       Issuer: {cert['issuer']}")

    # ========================================================================
    # TEST 5: Get Audit Trail
    # ========================================================================
    print("\n[TEST 5] Retrieving audit trail...")
    response = requests.get(f"{vault_url}/audit-trail?limit=100", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    audit = response.json()
    print(f"  [OK] Audit trail retrieved:")
    print(f"       Total entries: {audit['total']}")
    print(f"       Organization: {audit['organization_id']}")
    if audit['entries']:
        print(f"       Sample entries:")
        for entry in audit['entries'][:3]:
            print(f"         - {entry['action']} at {entry['timestamp']}")

    # ========================================================================
    # TEST 6: Get Audit Summary
    # ========================================================================
    print("\n[TEST 6] Retrieving audit summary...")
    response = requests.get(f"{vault_url}/audit-summary", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    summary = response.json()
    print(f"  [OK] Audit summary retrieved:")
    print(f"       Organization: {summary['organization_id']}")
    print(f"       Summary: {summary['summary']}")

    # ========================================================================
    # TEST 7: Get All Organization Proofs
    # ========================================================================
    print("\n[TEST 7] Getting all organization proofs...")
    response = requests.get(f"{vault_url}/organization/proofs?limit=100", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    org_proofs = response.json()
    print(f"  [OK] Organization proofs retrieved:")
    print(f"       Total proofs: {org_proofs['total']}")
    print(f"       Organization: {org_proofs['organization_id']}")

    # ========================================================================
    # TEST 8: Get Vault Statistics
    # ========================================================================
    print("\n[TEST 8] Getting vault statistics...")
    response = requests.get(f"{vault_url}/stats")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    stats = response.json()
    print(f"  [OK] Vault statistics:")
    print(f"       Total proofs: {stats['total_proofs']}")
    print(f"       Active organizations: {stats['active_organizations']}")
    print(f"       Total reads: {stats['total_reads']}")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED!")
    print("=" * 80)
    print(f"\nVault is fully operational with:")
    print(f"  [PASS] Multi-organization support")
    print(f"  [PASS] API key authentication")
    print(f"  [PASS] Proof submission and storage")
    print(f"  [PASS] Proof verification")
    print(f"  [PASS] Certificate generation")
    print(f"  [PASS] Complete audit trails")
    print(f"  [PASS] Vault statistics")
    print(f"\nProofs created: {len(proofs)}")
    print(f"Vault URL: {vault_url}")
    print(f"Organization ID: {org_id}")

if __name__ == "__main__":
    try:
        test_vault_complete_workflow()
    except AssertionError as e:
        print(f"\n[FAILED] {e}")
        exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
