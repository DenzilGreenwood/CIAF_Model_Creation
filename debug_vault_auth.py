#!/usr/bin/env python3
"""
Debug script for CIAF Vault authentication issues.
Tests the complete flow: org creation → key generation → verification.
"""

import sys
import hashlib
import sqlite3
from pathlib import Path

# Add CIAF vault to path
sys.path.insert(0, str(Path(__file__).parent))

from ciaf.vault.authentication import APIKeyManager

def debug_auth_flow():
    """Step-by-step debug of authentication flow."""

    print("=" * 70)
    print("CIAF VAULT AUTHENTICATION DEBUG")
    print("=" * 70)

    # Initialize manager
    auth = APIKeyManager()
    db_path = auth.db_path
    print(f"\n[OK] Initialized APIKeyManager")
    print(f"  Database: {db_path}")

    # Step 1: Create organization
    print("\n" + "=" * 70)
    print("STEP 1: CREATE ORGANIZATION")
    print("=" * 70)
    org_id = "debug_test_org_001"
    org = auth.create_organization(org_id, "Debug Test Organization")
    print(f"[OK] Created organization:")
    print(f"  org_id: {org.org_id}")
    print(f"  name: {org.name}")
    print(f"  created_at: {org.created_at}")

    # Verify organization in database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM organizations WHERE org_id = ?", (org_id,))
    db_org = cursor.fetchone()
    print(f"\n[OK] Verified in database:")
    print(f"  {db_org}")

    # Step 2: Create API key
    print("\n" + "=" * 70)
    print("STEP 2: CREATE API KEY")
    print("=" * 70)
    raw_key, key_obj = auth.create_api_key(org_id, "Debug key")
    print(f"[OK] Created API key:")
    print(f"  key_id: {key_obj.key_id}")
    print(f"  raw_key (first 20 chars): {raw_key[:20]}...")
    print(f"  key_prefix: {key_obj.key_prefix}")
    print(f"  key_hash (first 20 chars): {key_obj.key_hash[:20]}...")
    print(f"  is_active: {key_obj.is_active}")

    # Manually hash the raw key to verify SHA256
    manual_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    print(f"\n[OK] SHA256 Verification:")
    print(f"  Stored hash: {key_obj.key_hash}")
    print(f"  Manual hash: {manual_hash}")
    print(f"  Match: {key_obj.key_hash == manual_hash}")

    # Step 3: Query database directly
    print("\n" + "=" * 70)
    print("STEP 3: DATABASE QUERY")
    print("=" * 70)
    cursor.execute("""
        SELECT key_id, org_id, key_hash, key_prefix, is_active, expires_at
        FROM api_keys
        WHERE org_id = ?
    """, (org_id,))
    db_key = cursor.fetchone()
    print(f"[OK] API key in database:")
    print(f"  key_id: {db_key[0]}")
    print(f"  org_id: {db_key[1]}")
    print(f"  key_hash: {db_key[2][:20]}...")
    print(f"  key_prefix: {db_key[3]}")
    print(f"  is_active: {db_key[4]}")
    print(f"  expires_at: {db_key[5]}")

    # Query by hash
    cursor.execute("""
        SELECT key_id, org_id, is_active, expires_at
        FROM api_keys
        WHERE key_hash = ?
    """, (manual_hash,))
    hash_query = cursor.fetchone()
    print(f"\n[OK] Query by hash:")
    print(f"  Found: {hash_query is not None}")
    if hash_query:
        print(f"  Result: {hash_query}")

    conn.close()

    # Step 4: Call verify_api_key
    print("\n" + "=" * 70)
    print("STEP 4: API KEY VERIFICATION")
    print("=" * 70)
    result = auth.verify_api_key(raw_key)
    print(f"[OK] verify_api_key() result:")
    print(f"  Result: {result}")
    print(f"  Type: {type(result)}")
    if result:
        org_id_returned, key_id_returned = result
        print(f"  org_id: {org_id_returned}")
        print(f"  key_id: {key_id_returned}")

    # Step 5: Test with wrong key
    print("\n" + "=" * 70)
    print("STEP 5: TEST NEGATIVE CASE (Wrong Key)")
    print("=" * 70)
    wrong_result = auth.verify_api_key("definitely_not_a_real_key")
    print(f"[OK] verify_api_key(wrong_key) result:")
    print(f"  Result: {wrong_result}")
    print(f"  Expected: None")

    print("\n" + "=" * 70)
    print("DEBUG COMPLETE")
    print("=" * 70)

    return raw_key, key_obj

if __name__ == "__main__":
    raw_key, key_obj = debug_auth_flow()
    print(f"\nFor API testing, use:")
    print(f"  Authorization Header: Bearer {raw_key}")
    print(f"  Organization ID: {key_obj.org_id}")
    print(f"  Key ID: {key_obj.key_id}")
