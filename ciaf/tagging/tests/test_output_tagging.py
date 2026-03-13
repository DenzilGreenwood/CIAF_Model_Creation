"""
Quick test for Output Tagging System (Phase 2)

Run with: python -m pytest ciaf/tagging/tests/test_output_tagging.py -v
"""

import pytest
import json
from ciaf.tagging import OutputTag, OutputTagManager, TagEmbedder


class TestOutputTag:
    """Test OutputTag functionality."""

    def test_tag_creation(self):
        """Test creating an output tag."""
        tag = OutputTag(
            tag_id="test_tag_001",
            session_id="session_001",
            output_content_hash="abc123def456",
            inference_receipt_id="receipt_001",
            agent_ids=["agent_1", "agent_2"],
            organization_id="org_001",
            timestamp="2025-03-13T00:00:00",
        )

        assert tag.tag_id == "test_tag_001"
        assert tag.agent_ids == ["agent_1", "agent_2"]

    def test_tag_serialization(self):
        """Test tag serialization."""
        tag = OutputTag(
            tag_id="test_tag_001",
            session_id="session_001",
            output_content_hash="abc123",
            inference_receipt_id="receipt_001",
            agent_ids=["agent_1"],
            organization_id="org_001",
            timestamp="2025-03-13T00:00:00",
        )

        tag_dict = tag.to_dict()
        assert tag_dict["tag_id"] == "test_tag_001"

        tag_json = tag.to_json()
        assert isinstance(tag_json, str)
        assert "test_tag_001" in tag_json

    def test_minimal_dict(self):
        """Test minimal tag dict for embedding."""
        tag = OutputTag(
            tag_id="test_tag_001",
            session_id="session_001",
            output_content_hash="abc123",
            inference_receipt_id="receipt_001",
            agent_ids=["agent_1"],
            organization_id="org_001",
            timestamp="2025-03-13T00:00:00",
        )

        minimal = tag.to_minimal_dict()
        assert "tag_id" in minimal
        assert "session_id" in minimal
        assert "agent_ids" not in minimal  # Should not be in minimal

    def test_compute_hash(self):
        """Test hash computation."""
        content = "Hello, World!"
        hash1 = OutputTag.compute_hash(content)
        hash2 = OutputTag.compute_hash(content)

        # Hashes should be deterministic
        assert hash1 == hash2

        # With bytes
        hash3 = OutputTag.compute_hash(b"Hello, World!")
        assert hash1 == hash3

    def test_add_merkle_proofs(self):
        """Test adding merkle proofs to tag."""
        tag = OutputTag(
            tag_id="test_tag_001",
            session_id="session_001",
            output_content_hash="abc123",
            inference_receipt_id="receipt_001",
            agent_ids=["agent_1"],
            organization_id="org_001",
            timestamp="2025-03-13T00:00:00",
        )

        assert not tag.is_verified

        # Add task batch proof
        tag.add_task_batch_proof(
            task_batch_id="batch_001",
            merkle_root="root123",
            proof=[("sib1", "left"), ("sib2", "right")],
        )

        assert tag.task_batch_id == "batch_001"
        assert tag.task_batch_merkle_root == "root123"

        # Add org batch proof (marks verified)
        tag.add_org_batch_proof(
            org_batch_id="org_batch_001",
            merkle_root="org_root123",
            proof=[("org_sib1", "left")],
        )

        assert tag.org_batch_id == "org_batch_001"
        assert tag.is_verified


class TestOutputTagManager:
    """Test OutputTagManager functionality."""

    def test_create_agent_tag(self):
        """Test creating tags for agent inferences."""
        manager = OutputTagManager()

        tag = manager.create_agent_tag(
            output_content="Hello, World!",
            session_id="session_001",
            inference_receipt_id="receipt_001",
            agent_ids=["agent_1", "agent_2"],
            organization_id="org_001",
            policies_applied=["policy_1"],
        )

        assert tag.tag_id is not None
        assert tag.output_content_hash is not None
        assert tag.inference_type == "agent_orchestrated"
        assert tag.agent_ids == ["agent_1", "agent_2"]
        assert tag.model_name is None
        assert len(manager.tags) == 1

    def test_create_model_tag(self):
        """Test creating tags for direct model inferences."""
        manager = OutputTagManager()

        tag = manager.create_model_tag(
            output_content="Model prediction",
            session_id="session_001",
            inference_receipt_id="receipt_001",
            model_name="llama2-7b",
            organization_id="org_001",
            policies_applied=["policy_1"],
        )

        assert tag.tag_id is not None
        assert tag.inference_type == "direct_model"
        assert tag.model_name == "llama2-7b"
        assert tag.agent_ids == []
        assert len(manager.tags) == 1

    def test_create_tag_auto_detect(self):
        """Test generic create_tag with auto-detection."""
        manager = OutputTagManager()

        # Agent tag
        agent_tag = manager.create_tag(
            output_content="Agent output",
            session_id="session_001",
            inference_receipt_id="receipt_001",
            organization_id="org_001",
            agent_ids=["agent_1"],
        )
        assert agent_tag.inference_type == "agent_orchestrated"

        # Model tag
        model_tag = manager.create_tag(
            output_content="Model output",
            session_id="session_001",
            inference_receipt_id="receipt_002",
            organization_id="org_001",
            model_name="gpt4_turbo",
        )
        assert model_tag.inference_type == "direct_model"

    def test_retrieve_tag(self):
        """Test retrieving tags."""
        manager = OutputTagManager()

        tag1 = manager.create_tag(
            output_content="Content 1",
            session_id="session_001",
            inference_receipt_id="receipt_001",
            agent_ids=["agent_1"],
            organization_id="org_001",
        )

        retrieved = manager.get_tag(tag1.tag_id)
        assert retrieved is not None
        assert retrieved.tag_id == tag1.tag_id

    def test_session_tags(self):
        """Test getting tags by session."""
        manager = OutputTagManager()

        for i in range(3):
            manager.create_tag(
                output_content=f"Content {i}",
                session_id="session_001",
                inference_receipt_id=f"receipt_{i}",
                agent_ids=["agent_1"],
                organization_id="org_001",
            )

        tags = manager.get_session_tags("session_001")
        assert len(tags) == 3

    def test_add_proofs(self):
        """Test adding merkle proofs."""
        manager = OutputTagManager()

        tag = manager.create_agent_tag(
            output_content="Content",
            session_id="session_001",
            inference_receipt_id="receipt_001",
            agent_ids=["agent_1"],
            organization_id="org_001",
        )

        # Add task batch proof
        manager.add_task_batch_proof(
            tag.tag_id,
            "batch_001",
            "root123",
            [("sib1", "left")],
        )

        updated = manager.get_tag(tag.tag_id)
        assert updated.task_batch_id == "batch_001"

    def test_get_tags_by_agent(self):
        """Test retrieving tags by agent."""
        manager = OutputTagManager()

        tag1 = manager.create_agent_tag(
            output_content="Content 1",
            session_id="session_001",
            inference_receipt_id="receipt_001",
            agent_ids=["agent_1"],
            organization_id="org_001",
        )

        tag2 = manager.create_agent_tag(
            output_content="Content 2",
            session_id="session_001",
            inference_receipt_id="receipt_002",
            agent_ids=["agent_1", "agent_2"],
            organization_id="org_001",
        )

        agent1_tags = manager.get_agent_tags("agent_1")
        assert len(agent1_tags) == 2

        agent2_tags = manager.get_agent_tags("agent_2")
        assert len(agent2_tags) == 1

    def test_get_tags_by_model(self):
        """Test retrieving tags by model."""
        manager = OutputTagManager()

        tag1 = manager.create_model_tag(
            output_content="Output 1",
            session_id="session_001",
            inference_receipt_id="receipt_001",
            model_name="llama2-7b",
            organization_id="org_001",
        )

        tag2 = manager.create_model_tag(
            output_content="Output 2",
            session_id="session_001",
            inference_receipt_id="receipt_002",
            model_name="llama2-7b",
            organization_id="org_001",
        )

        tag3 = manager.create_model_tag(
            output_content="Output 3",
            session_id="session_001",
            inference_receipt_id="receipt_003",
            model_name="gpt4_turbo",
            organization_id="org_001",
        )

        llama_tags = manager.get_model_tags("llama2-7b")
        assert len(llama_tags) == 2

        gpt_tags = manager.get_model_tags("gpt4_turbo")
        assert len(gpt_tags) == 1

class TestTagEmbedder:
    """Test tag embedding in different formats."""

    def test_embed_json_comment(self):
        """Test embedding in JSON comment format."""
        tag = OutputTag(
            tag_id="tag_001",
            session_id="session_001",
            output_content_hash="hash123",
            inference_receipt_id="receipt_001",
            agent_ids=["agent_1"],
            organization_id="org_001",
            timestamp="2025-03-13T00:00:00",
        )

        output = "Hello, World!"
        embedded = TagEmbedder.embed_in_text(output, tag, format="json_comment")

        assert "<!-- CIAF Output Tag" in embedded
        assert "tag_001" in embedded
        assert output in embedded

    def test_extract_json_comment(self):
        """Test extracting tag from JSON comment."""
        tag = OutputTag(
            tag_id="tag_001",
            session_id="session_001",
            output_content_hash="hash123",
            inference_receipt_id="receipt_001",
            agent_ids=["agent_1"],
            organization_id="org_001",
            timestamp="2025-03-13T00:00:00",
        )

        output = "Hello, World!"
        embedded = TagEmbedder.embed_in_text(output, tag, format="json_comment")

        extracted = TagEmbedder.extract_tag_from_text(embedded)
        assert extracted is not None
        assert extracted.tag_id == tag.tag_id

    def test_embed_hidden_metadata(self):
        """Test embedding as hidden metadata."""
        tag = OutputTag(
            tag_id="tag_001",
            session_id="session_001",
            output_content_hash="hash123",
            inference_receipt_id="receipt_001",
            agent_ids=["agent_1"],
            organization_id="org_001",
            timestamp="2025-03-13T00:00:00",
        )

        output = "Hello, World!"
        embedded = TagEmbedder.embed_in_text(output, tag, format="hidden_metadata")

        assert "[METADATA]" in embedded
        assert output in embedded

    def test_extract_hidden_metadata(self):
        """Test extracting from hidden metadata."""
        tag = OutputTag(
            tag_id="tag_001",
            session_id="session_001",
            output_content_hash="hash123",
            inference_receipt_id="receipt_001",
            agent_ids=["agent_1"],
            organization_id="org_001",
            timestamp="2025-03-13T00:00:00",
        )

        output = "Hello, World!"
        embedded = TagEmbedder.embed_in_text(output, tag, format="hidden_metadata")

        extracted = TagEmbedder.extract_tag_from_text(embedded)
        assert extracted is not None
        assert extracted.tag_id == tag.tag_id

    def test_embed_structured(self):
        """Test embedding in structured data."""
        tag = OutputTag(
            tag_id="tag_001",
            session_id="session_001",
            output_content_hash="hash123",
            inference_receipt_id="receipt_001",
            agent_ids=["agent_1"],
            organization_id="org_001",
            timestamp="2025-03-13T00:00:00",
        )

        data = {"result": "Hello", "score": 0.95}
        embedded = TagEmbedder.embed_in_structured(data, tag)

        assert "_ciaf_tag" in embedded
        assert embedded["result"] == "Hello"
        assert embedded["score"] == 0.95

    def test_extract_structured(self):
        """Test extracting from structured data."""
        tag = OutputTag(
            tag_id="tag_001",
            session_id="session_001",
            output_content_hash="hash123",
            inference_receipt_id="receipt_001",
            agent_ids=["agent_1"],
            organization_id="org_001",
            timestamp="2025-03-13T00:00:00",
        )

        data = {"result": "Hello", "score": 0.95}
        embedded = TagEmbedder.embed_in_structured(data, tag)

        extracted = TagEmbedder.extract_tag_from_structured(embedded)
        assert extracted is not None
        assert extracted.tag_id == tag.tag_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
