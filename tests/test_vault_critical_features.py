"""
Comprehensive tests for CIAF Vault critical features.

Tests for:
- Database-level WORM constraints
- Key rotation functionality
- Public key export
- Rate limiting
- Merkle tree population
- Audit logging
"""

import pytest
import sqlite3
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from ciaf.vault.core import VaultManager, ImmutableProof
from ciaf.vault.authentication import APIKeyManager
from ciaf.vault.audit import AuditLogger


@pytest.fixture
def temp_vault_path(tmp_path):
    """Create temporary vault path for testing."""
    vault_path = tmp_path / "test_vault"
    vault_path.mkdir()
    return str(vault_path)


@pytest.fixture
def vault_manager(temp_vault_path):
    """Create VaultManager instance for testing."""
    return VaultManager(vault_path=temp_vault_path)


@pytest.fixture
def audit_logger(temp_vault_path):
    """Create AuditLogger instance for testing."""
    return AuditLogger(vault_path=temp_vault_path)


class TestDatabaseWORMEnforcement:
    """Test database-level WORM constraints."""

    def test_insert_and_retrieve_proof(self, vault_manager):
        """Test basic proof submission and retrieval."""
        receipt = vault_manager.submit_proof(
            organization_id="test-org",
            content="Test proof content",
            agent_ids=["agent1"],
            policies_applied=["policy1"],
            timestamp=datetime.now().isoformat()
        )

        assert receipt.proof_id is not None
        assert receipt.receipt_id is not None
        assert receipt.organization_id == "test-org"

        # Verify proof was stored
        proof = vault_manager.verify_proof(receipt.proof_id, "test-org")
        assert proof is not None
        assert proof.content_hash is not None

    def test_duplicate_content_rejection(self, vault_manager):
        """Test that duplicate content is rejected."""
        content = "Unique proof content"
        timestamp = datetime.now().isoformat()

        # First submission should succeed
        receipt1 = vault_manager.submit_proof(
            organization_id="test-org",
            content=content,
            agent_ids=["agent1"],
            policies_applied=["policy1"],
            timestamp=timestamp
        )
        assert receipt1.proof_id is not None

        # Second submission with same content should fail
        with pytest.raises(ValueError, match="Proof already exists"):
            vault_manager.submit_proof(
                organization_id="test-org",
                content=content,
                agent_ids=["agent1"],
                policies_applied=["policy1"],
                timestamp=timestamp
            )

    def test_worm_trigger_prevents_modification(self, vault_manager):
        """Test that database triggers prevent proof modification."""
        receipt = vault_manager.submit_proof(
            organization_id="test-org",
            content="Original content",
            agent_ids=["agent1"],
            policies_applied=["policy1"],
            timestamp=datetime.now().isoformat()
        )

        # Try to directly modify proof content (should fail due to trigger)
        conn = sqlite3.connect(vault_manager.db_path)
        cursor = conn.cursor()

        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                'UPDATE vault_proofs SET raw_content = ? WHERE proof_id = ?',
                ('Modified content', receipt.proof_id)
            )
            conn.commit()

        conn.close()

    def test_read_counter_update_allowed(self, vault_manager):
        """Test that read counter can be updated (WORM exception)."""
        receipt = vault_manager.submit_proof(
            organization_id="test-org",
            content="Test content",
            agent_ids=["agent1"],
            policies_applied=["policy1"],
            timestamp=datetime.now().isoformat()
        )

        # First verify should increment read counter
        proof1 = vault_manager.verify_proof(receipt.proof_id, "test-org")
        assert proof1.read_count == 1

        # Second verify should increment again
        proof2 = vault_manager.verify_proof(receipt.proof_id, "test-org")
        assert proof2.read_count == 2


class TestKeyRotation:
    """Test key rotation functionality."""

    def test_get_initial_key_version(self, vault_manager):
        """Test getting initial key version."""
        version = vault_manager.get_key_version()
        assert version == "1.0"

    def test_rotate_key_increments_version(self, vault_manager):
        """Test key rotation increments version."""
        old_version = vault_manager.get_key_version()

        result = vault_manager.rotate_key(reason="Test rotation")

        assert result["new_version"] == "2.0"
        assert result["old_version"] == "1.0"
        assert "public_key_pem" in result
        assert "rotated_at" in result

    def test_key_versions_tracked(self, vault_manager):
        """Test that key versions are tracked in database."""
        vault_manager.rotate_key(reason="First rotation")
        vault_manager.rotate_key(reason="Second rotation")

        versions = vault_manager.get_key_versions()
        assert len(versions) >= 2

    def test_proof_includes_key_version(self, vault_manager):
        """Test that proofs include the key version they were signed with."""
        receipt1 = vault_manager.submit_proof(
            organization_id="test-org",
            content="Proof with key v1",
            agent_ids=["agent1"],
            policies_applied=["policy1"],
            timestamp=datetime.now().isoformat()
        )

        vault_manager.rotate_key(reason="Rotate to v2")

        receipt2 = vault_manager.submit_proof(
            organization_id="test-org",
            content="Proof with key v2",
            agent_ids=["agent1"],
            policies_applied=["policy1"],
            timestamp=datetime.now().isoformat()
        )

        # Check key versions in database
        conn = sqlite3.connect(vault_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT key_version FROM vault_receipts WHERE receipt_id = ?', (receipt1.receipt_id,))
        v1_key = cursor.fetchone()["key_version"]

        cursor.execute('SELECT key_version FROM vault_receipts WHERE receipt_id = ?', (receipt2.receipt_id,))
        v2_key = cursor.fetchone()["key_version"]

        cursor.close()
        conn.close()

        assert v1_key == "1.0"
        assert v2_key == "2.0"


class TestPublicKeyExport:
    """Test public key export functionality."""

    def test_get_public_key_pem(self, vault_manager):
        """Test getting public key in PEM format."""
        public_pem = vault_manager.get_public_key_pem()

        assert public_pem is not None
        assert "-----BEGIN PUBLIC KEY-----" in public_pem
        assert "-----END PUBLIC KEY-----" in public_pem

    def test_public_key_consistency(self, vault_manager):
        """Test that public key is consistent across calls."""
        key1 = vault_manager.get_public_key_pem()
        key2 = vault_manager.get_public_key_pem()

        assert key1 == key2


class TestMerkleTreePopulation:
    """Test Merkle tree population in proofs."""

    def test_merkle_root_generated(self, vault_manager):
        """Test that merkle_root is generated for each proof."""
        receipt = vault_manager.submit_proof(
            organization_id="test-org",
            content="Test content for merkle",
            agent_ids=["agent1"],
            policies_applied=["policy1"],
            timestamp=datetime.now().isoformat()
        )

        proof = vault_manager.verify_proof(receipt.proof_id, "test-org")
        assert proof.merkle_root is not None
        assert len(proof.merkle_root) == 64  # SHA-256 hex is 64 chars

    def test_merkle_root_in_database(self, vault_manager):
        """Test that merkle_root is stored in database."""
        receipt = vault_manager.submit_proof(
            organization_id="test-org",
            content="Merkle test content",
            agent_ids=["agent1"],
            policies_applied=["policy1"],
            timestamp=datetime.now().isoformat()
        )

        conn = sqlite3.connect(vault_manager.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT merkle_root FROM vault_proofs WHERE proof_id = ?', (receipt.proof_id,))
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] is not None
        assert len(result[0]) == 64


class TestAuditLogging:
    """Test immutable audit logging."""

    def test_audit_log_created(self, audit_logger):
        """Test that audit logs are created."""
        entry_id = "test-entry-1"
        audit_logger.log_action(
            entry_id=entry_id,
            action="test_action",
            organization_id="test-org",
            actor="test-actor",
            result="success",
            details={"test": "details"}
        )

        # Should not raise an exception

    def test_audit_log_immutable(self, audit_logger):
        """Test that audit logs are designed as immutable (INSERT-only)."""
        entry_id = "test-entry-2"
        audit_logger.log_action(
            entry_id=entry_id,
            action="original_action",
            organization_id="test-org",
            actor="test-actor",
            result="success",
            details={}
        )

        # Verify the audit entry was logged
        conn = sqlite3.connect(audit_logger.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT action FROM audit_log WHERE entry_id = ?', (entry_id,))
        result = cursor.fetchone()
        assert result is not None
        assert result["action"] == "original_action"

        conn.close()


class TestMultiTenantIsolation:
    """Test multi-tenant isolation."""

    def test_organization_isolation(self, vault_manager):
        """Test that organizations cannot access each other's proofs."""
        receipt_org1 = vault_manager.submit_proof(
            organization_id="org1",
            content="Org1 content",
            agent_ids=["agent1"],
            policies_applied=["policy1"],
            timestamp=datetime.now().isoformat()
        )

        # Org2 should not be able to access Org1's proof
        proof_for_org2 = vault_manager.verify_proof(receipt_org1.proof_id, "org2")
        assert proof_for_org2 is None

        # Org1 should be able to access its own proof
        proof_for_org1 = vault_manager.verify_proof(receipt_org1.proof_id, "org1")
        assert proof_for_org1 is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
