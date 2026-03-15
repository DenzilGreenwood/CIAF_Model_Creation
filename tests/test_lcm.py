"""
Backend Unit Tests - LCM (Lazy Capsule Materialization) System
Tests for proof generation, materialization, verification
"""
import pytest
from datetime import datetime
from typing import Dict, Any
import hashlib
import json


class LCMProof:
    """Represent a cryptographic proof"""

    def __init__(self, content_hash: str, timestamp: str, signature: str):
        self.content_hash = content_hash
        self.timestamp = timestamp
        self.signature = signature
        self.verified = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content_hash": self.content_hash,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "verified": self.verified
        }


class LCMSystem:
    """Lazy Capsule Materialization system"""

    @staticmethod
    def compute_hash(content: str) -> str:
        """Compute SHA-256 hash of content"""
        return hashlib.sha256(content.encode()).hexdigest()

    @staticmethod
    def create_proof(content: str) -> LCMProof:
        """Create a proof for content"""
        content_hash = LCMSystem.compute_hash(content)
        timestamp = datetime.utcnow().isoformat()
        # Simplified signature (in production, use Ed25519)
        signature = hashlib.sha256(
            f"{content_hash}{timestamp}".encode()
        ).hexdigest()

        return LCMProof(content_hash, timestamp, signature)

    @staticmethod
    def verify_proof(proof: LCMProof, original_content: str) -> bool:
        """Verify a proof matches the original content"""
        expected_hash = LCMSystem.compute_hash(original_content)
        expected_signature = hashlib.sha256(
            f"{expected_hash}{proof.timestamp}".encode()
        ).hexdigest()

        is_valid = (
            proof.content_hash == expected_hash and
            proof.signature == expected_signature
        )
        proof.verified = is_valid
        return is_valid

    @staticmethod
    def materialize_proof(proof: LCMProof) -> Dict[str, Any]:
        """Materialize a proof (lazy evaluation)"""
        return {
            "proof": proof.to_dict(),
            "materialized_at": datetime.utcnow().isoformat(),
            "status": "verified" if proof.verified else "unverified"
        }


# ========== TESTS ==========

class TestHashComputation:
    """Test SHA-256 hash computation"""

    def test_compute_hash_returns_string(self):
        content = "test content"
        hash_value = LCMSystem.compute_hash(content)
        assert isinstance(hash_value, str)

    def test_compute_hash_is_deterministic(self):
        content = "consistent content"
        hash1 = LCMSystem.compute_hash(content)
        hash2 = LCMSystem.compute_hash(content)
        assert hash1 == hash2

    def test_different_content_produces_different_hash(self):
        hash1 = LCMSystem.compute_hash("content1")
        hash2 = LCMSystem.compute_hash("content2")
        assert hash1 != hash2

    def test_hash_length_is_64_characters(self):
        # SHA-256 produces 64 hex characters
        hash_value = LCMSystem.compute_hash("any content")
        assert len(hash_value) == 64

    def test_small_change_completely_changes_hash(self):
        hash1 = LCMSystem.compute_hash("The quick brown fox")
        hash2 = LCMSystem.compute_hash("The quick brown fox.")  # Added period
        assert hash1 != hash2


class TestProofCreation:
    """Test proof creation"""

    def test_create_proof_returns_lcm_proof(self):
        proof = LCMSystem.create_proof("test content")
        assert isinstance(proof, LCMProof)

    def test_proof_contains_all_required_fields(self):
        proof = LCMSystem.create_proof("test")
        assert proof.content_hash is not None
        assert proof.timestamp is not None
        assert proof.signature is not None

    def test_proof_initially_unverified(self):
        proof = LCMSystem.create_proof("test")
        assert proof.verified is False

    def test_multiple_proofs_have_different_timestamps(self):
        import time
        proof1 = LCMSystem.create_proof("content")
        time.sleep(0.01)
        proof2 = LCMSystem.create_proof("content")
        # Same content, but different timestamps should give different signatures
        assert proof1.signature != proof2.signature

    def test_proof_to_dict_conversion(self):
        proof = LCMSystem.create_proof("test")
        proof_dict = proof.to_dict()
        assert "content_hash" in proof_dict
        assert "timestamp" in proof_dict
        assert "signature" in proof_dict
        assert "verified" in proof_dict


class TestProofVerification:
    """Test proof verification"""

    def test_verify_valid_proof_returns_true(self):
        content = "important data"
        proof = LCMSystem.create_proof(content)
        assert LCMSystem.verify_proof(proof, content)

    def test_verify_proof_sets_verified_flag(self):
        content = "data to verify"
        proof = LCMSystem.create_proof(content)
        LCMSystem.verify_proof(proof, content)
        assert proof.verified is True

    def test_verify_proof_with_modified_content_fails(self):
        content = "original content"
        proof = LCMSystem.create_proof(content)
        modified_content = "modified content"
        assert not LCMSystem.verify_proof(proof, modified_content)

    def test_verify_proof_with_modified_content_unsets_flag(self):
        content = "original"
        proof = LCMSystem.create_proof(content)
        LCMSystem.verify_proof(proof, "modified")
        assert proof.verified is False

    def test_verify_tamperedproof_with_wrong_hash(self):
        content = "original"
        proof = LCMSystem.create_proof(content)
        # Tamper with hash
        proof.content_hash = "0" * 64
        assert not LCMSystem.verify_proof(proof, content)

    def test_verify_tampered_proof_with_wrong_signature(self):
        content = "original"
        proof = LCMSystem.create_proof(content)
        # Tamper with signature
        proof.signature = "a" * 64
        assert not LCMSystem.verify_proof(proof, content)


class TestProofMaterialization:
    """Test lazy proof materialization"""

    def test_materialize_proof_returns_dict(self):
        proof = LCMSystem.create_proof("test")
        LCMSystem.verify_proof(proof, "test")
        materialized = LCMSystem.materialize_proof(proof)
        assert isinstance(materialized, dict)

    def test_materialized_proof_contains_timestamp(self):
        proof = LCMSystem.create_proof("test")
        materialized = LCMSystem.materialize_proof(proof)
        assert "materialized_at" in materialized

    def test_materialized_proof_shows_verified_status(self):
        content = "test"
        proof = LCMSystem.create_proof(content)
        LCMSystem.verify_proof(proof, content)
        materialized = LCMSystem.materialize_proof(proof)
        assert materialized["status"] == "verified"

    def test_materialized_unverified_proof_shows_unverified_status(self):
        proof = LCMSystem.create_proof("test")
        # Don't verify
        materialized = LCMSystem.materialize_proof(proof)
        assert materialized["status"] == "unverified"

    def test_materialized_proof_includes_full_proof_data(self):
        proof = LCMSystem.create_proof("test")
        materialized = LCMSystem.materialize_proof(proof)
        assert "proof" in materialized
        assert "content_hash" in materialized["proof"]
        assert "signature" in materialized["proof"]


class TestLCMCompleteFlow:
    """Test complete LCM workflow"""

    def test_end_to_end_proof_generation_and_verification(self):
        # Step 1: Create proof for output
        output = "Model prediction: class A with 95% confidence"
        proof = LCMSystem.create_proof(output)

        # Step 2: Verify proof
        assert LCMSystem.verify_proof(proof, output)
        assert proof.verified is True

        # Step 3: Materialize proof
        materialized = LCMSystem.materialize_proof(proof)
        assert materialized["status"] == "verified"

    def test_proof_chain_integrity(self):
        # Create multiple proofs
        outputs = [
            "First inference output",
            "Second inference output",
            "Third inference output"
        ]

        proofs = [LCMSystem.create_proof(output) for output in outputs]

        # Verify all proofs
        for proof, output in zip(proofs, outputs):
            assert LCMSystem.verify_proof(proof, output)

        # All should be verified
        assert all(p.verified for p in proofs)

    def test_tampering_detection(self):
        output = "Clean output"
        proof = LCMSystem.create_proof(output)

        # Verify initially works
        assert LCMSystem.verify_proof(proof, output)

        # Try to tamper
        tampered_output = "Tampered output"
        assert not LCMSystem.verify_proof(proof, tampered_output)


# ========== RUNS WITH: pytest tests/test_lcm.py ==========
