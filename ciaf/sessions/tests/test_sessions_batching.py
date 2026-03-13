"""
Tests for Session & Task Batching System (Phase 3)

Run with: python -m pytest ciaf/sessions/tests/test_sessions_batching.py -v
"""

import pytest
from ciaf.sessions import TaskBatch, SessionBatcher, AgentSession
from ciaf.tagging import OutputTagManager


class TestTaskBatch:
    """Test TaskBatch functionality."""

    def test_batch_creation(self):
        """Test creating a task batch."""
        batch = TaskBatch(
            task_batch_id="batch_001",
            session_id="session_001",
            organization_id="org_001",
        )

        assert batch.task_batch_id == "batch_001"
        assert batch.status == "success"
        assert len(batch.output_tag_ids) == 0

    def test_add_output_tag(self):
        """Test adding output tags to batch."""
        batch = TaskBatch(
            task_batch_id="batch_001",
            session_id="session_001",
            organization_id="org_001",
        )

        batch.add_output_tag("tag_001")
        batch.add_output_tag("tag_002")

        assert len(batch.output_tag_ids) == 2
        assert "tag_001" in batch.output_tag_ids

    def test_batch_finalization(self):
        """Test finalizing batch."""
        batch = TaskBatch(
            task_batch_id="batch_001",
            session_id="session_001",
            organization_id="org_001",
        )

        batch.add_output_tag("tag_001")
        batch.finalize(status="success")

        assert batch.status == "success"
        assert batch.end_time is not None
        assert batch.duration_ms is not None
        assert batch.content_hash != ""

    def test_content_hash_determinism(self):
        """Test that content hash is deterministic."""
        batch1 = TaskBatch(
            task_batch_id="batch_001",
            session_id="session_001",
            organization_id="org_001",
        )
        batch1.add_output_tag("tag_001")
        batch1.add_output_tag("tag_002")

        batch2 = TaskBatch(
            task_batch_id="batch_001",
            session_id="session_001",
            organization_id="org_001",
        )
        batch2.add_output_tag("tag_002")
        batch2.add_output_tag("tag_001")  # Different order

        # Should produce same hash (tags are sorted)
        hash1 = batch1.compute_content_hash()
        hash2 = batch2.compute_content_hash()
        assert hash1 == hash2


class TestSessionBatcher:
    """Test SessionBatcher functionality."""

    def test_new_task(self):
        """Test creating new task."""
        tag_manager = OutputTagManager()
        batcher = SessionBatcher(tag_manager)

        batch = batcher.new_task(
            session_id="session_001",
            organization_id="org_001",
            task_description="Test task",
        )

        assert batch.session_id == "session_001"
        assert batch.task_description == "Test task"
        assert batcher.get_batch(batch.task_batch_id) is not None

    def test_add_output_to_task(self):
        """Test adding output tags to task."""
        tag_manager = OutputTagManager()
        batcher = SessionBatcher(tag_manager)

        batch = batcher.new_task("session_001", "org_001")

        success = batcher.add_output_to_task(batch.task_batch_id, "tag_001")
        assert success

        batch = batcher.get_batch(batch.task_batch_id)
        assert "tag_001" in batch.output_tag_ids

    def test_complete_task_with_merkle(self):
        """Test completing task creates merkle tree."""
        tag_manager = OutputTagManager()
        batcher = SessionBatcher(tag_manager)

        # Create tags
        tag1 = tag_manager.create_model_tag(
            output_content="Output 1",
            session_id="session_001",
            inference_receipt_id="receipt_001",
            model_name="model_1",
            organization_id="org_001",
        )

        tag2 = tag_manager.create_model_tag(
            output_content="Output 2",
            session_id="session_001",
            inference_receipt_id="receipt_002",
            model_name="model_1",
            organization_id="org_001",
        )

        # Create task and add tags
        batch = batcher.new_task("session_001", "org_001")
        batcher.add_output_to_task(batch.task_batch_id, tag1.tag_id)
        batcher.add_output_to_task(batch.task_batch_id, tag2.tag_id)

        # Complete task (creates merkle tree)
        success, merkle_root = batcher.complete_task(batch.task_batch_id)

        assert success
        assert merkle_root is not None

        # Check that tags have merkle proofs
        updated_tag1 = tag_manager.get_tag(tag1.tag_id)
        assert updated_tag1.task_batch_id == batch.task_batch_id
        assert updated_tag1.task_batch_merkle_root == merkle_root
        assert updated_tag1.task_batch_proof is not None

    def test_session_stats(self):
        """Test getting session statistics."""
        tag_manager = OutputTagManager()
        batcher = SessionBatcher(tag_manager)

        # Create 2 tasks
        for task_num in range(2):
            batch = batcher.new_task(
                "session_001",
                "org_001",
                f"Task {task_num+1}",
            )

            # Add 2 tags per task
            for i in range(2):
                tag = tag_manager.create_model_tag(
                    output_content=f"Output {task_num}_{i}",
                    session_id="session_001",
                    inference_receipt_id=f"receipt_{task_num}_{i}",
                    model_name="model_1",
                    organization_id="org_001",
                )
                batcher.add_output_to_task(batch.task_batch_id, tag.tag_id)

            batcher.complete_task(batch.task_batch_id)

        stats = batcher.get_stats_for_session("session_001")
        assert stats["batch_count"] == 2
        assert stats["total_outputs"] == 4
        assert stats["status_distribution"]["success"] == 2


class TestAgentSession:
    """Test AgentSession functionality."""

    def test_session_creation(self):
        """Test creating session."""
        session = AgentSession(
            session_id="session_001",
            user_id="user_123",
            organization_id="org_001",
        )

        assert session.session_id == "session_001"
        assert session.user_id == "user_123"
        assert session.current_task is None

    def test_start_task(self):
        """Test starting a task."""
        session = AgentSession(
            session_id="session_001",
            user_id="user_123",
            organization_id="org_001",
        )

        task = session.start_task("Analyze data")
        assert task is not None
        assert session.current_task == task

    def test_record_model_output(self):
        """Test recording model output."""
        session = AgentSession(
            session_id="session_001",
            user_id="user_123",
            organization_id="org_001",
        )

        session.start_task("Classify sentiment")

        tag = session.record_output(
            output_content="Positive sentiment (0.92)",
            inference_receipt_id="receipt_001",
            model_name="sentiment_bert",
            policies_applied=["CONTENT_POLICY"],
        )

        assert tag is not None
        assert tag.model_name == "sentiment_bert"
        assert tag.inference_type == "direct_model"

    def test_record_agent_output(self):
        """Test recording agent output."""
        session = AgentSession(
            session_id="session_001",
            user_id="user_123",
            organization_id="org_001",
        )

        session.start_task("Complex analysis")

        tag = session.record_output(
            output_content="Recommendation: Buy",
            inference_receipt_id="receipt_001",
            agent_ids=["analyst_agent_001", "decision_agent_001"],
            policies_applied=["FAIR_LENDING"],
            risk_level="high",
        )

        assert tag is not None
        assert tag.inference_type == "agent_orchestrated"
        assert len(tag.agent_ids) == 2

    def test_complete_task_creates_merkle(self):
        """Test completing task creates merkle proofs."""
        session = AgentSession(
            session_id="session_001",
            user_id="user_123",
            organization_id="org_001",
        )

        session.start_task("Multi-step analysis")

        # Record multiple outputs
        tag1 = session.record_output(
            output_content="Step 1: Extract features",
            inference_receipt_id="receipt_001",
            model_name="feature_extractor",
        )

        tag2 = session.record_output(
            output_content="Step 2: Classify",
            inference_receipt_id="receipt_002",
            model_name="classifier",
        )

        # Complete task
        completed = session.complete_current_task("success")

        assert completed is not None
        assert len(completed.output_tag_ids) == 2

        # Check merkle proofs
        updated_tag1 = session.tag_manager.get_tag(tag1.tag_id)
        assert updated_tag1.task_batch_merkle_root is not None
        assert updated_tag1.task_batch_proof is not None

    def test_multiple_tasks_in_session(self):
        """Test multiple tasks in single session."""
        session = AgentSession(
            session_id="session_001",
            user_id="user_123",
            organization_id="org_001",
        )

        # Task 1
        session.start_task("Task 1")
        session.record_output(
            output_content="Output 1",
            inference_receipt_id="receipt_1",
            model_name="model_1",
        )
        session.complete_current_task()

        # Task 2
        session.start_task("Task 2")
        session.record_output(
            output_content="Output 2",
            inference_receipt_id="receipt_2",
            model_name="model_1",
        )
        session.complete_current_task()

        session.end_session()

        summary = session.get_session_summary()
        assert summary["completed_tasks"] == 2
        assert summary["total_outputs"] == 2

    def test_session_summary(self):
        """Test session summary generation."""
        session = AgentSession(
            session_id="session_001",
            user_id="user_123",
            organization_id="org_001",
        )

        session.start_task("Test task")
        session.record_output(
            output_content="Output",
            inference_receipt_id="receipt_001",
            model_name="model_1",
        )
        session.complete_current_task()
        session.end_session()

        summary = session.get_session_summary()
        assert summary["session_id"] == "session_001"
        assert summary["completed_tasks"] == 1
        assert summary["total_outputs"] == 1
        assert summary["ended_at"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
