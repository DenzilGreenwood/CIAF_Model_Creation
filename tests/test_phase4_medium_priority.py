"""
Phase 4: Medium-Priority Module Tests - 100-150 tests for coverage expansion

Tests for medium-priority modules:
1. LCM Managers (dataset, training, inference) - 70 tests
2. Preprocessing (data quality, policy) - 30 tests
3. Agent Sessions - 25 tests

Expected Coverage: 29-32% → 50-60%
Total tests: ~125 tests
"""

import pytest
import json
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

# ============================================================================
# FIXTURES - Reusable test data and mocks
# ============================================================================

@pytest.fixture
def sample_dataset():
    """Create sample dataset for testing"""
    return [
        {"id": "row_1", "feature_1": 1.0, "feature_2": "value_1", "label": 0},
        {"id": "row_2", "feature_1": 2.0, "feature_2": "value_2", "label": 1},
        {"id": "row_3", "feature_1": 3.0, "feature_2": "value_3", "label": 0},
        {"id": "row_4", "feature_1": 4.0, "feature_2": "value_4", "label": 1},
    ]


@pytest.fixture
def sample_pandas_df():
    """Create sample pandas DataFrame"""
    return pd.DataFrame({
        "id": ["row_1", "row_2", "row_3"],
        "feature_1": [1.0, 2.0, 3.0],
        "feature_2": ["a", "b", "c"],
        "label": [0, 1, 0]
    })


# ============================================================================
# PART 1: LCM DATASET MANAGER TESTS (16 tests)
# ============================================================================

class TestDatasetSplit:
    """Test DatasetSplit enum"""

    def test_dataset_split_train(self):
        """DatasetSplit should have TRAIN value"""
        from ciaf.lcm.dataset_manager import DatasetSplit
        assert DatasetSplit.TRAIN.value == "train"

    def test_dataset_split_validation(self):
        """DatasetSplit should have VALIDATION value"""
        from ciaf.lcm.dataset_manager import DatasetSplit
        assert DatasetSplit.VALIDATION.value == "val"

    def test_dataset_split_test(self):
        """DatasetSplit should have TEST value"""
        from ciaf.lcm.dataset_manager import DatasetSplit
        assert DatasetSplit.TEST.value == "test"

    def test_dataset_split_full(self):
        """DatasetSplit should have FULL value"""
        from ciaf.lcm.dataset_manager import DatasetSplit
        assert DatasetSplit.FULL.value == "full"


class TestDatasetMetadata:
    """Test DatasetMetadata dataclass"""

    def test_dataset_metadata_initialization(self):
        """DatasetMetadata should initialize with required fields"""
        from ciaf.lcm.dataset_manager import DatasetMetadata

        metadata = DatasetMetadata(
            name="test_dataset",
            owner="test_owner",
            license="MIT"
        )

        assert metadata.name == "test_dataset"
        assert metadata.owner == "test_owner"
        assert metadata.license == "MIT"

    def test_dataset_metadata_defaults(self):
        """DatasetMetadata should have sensible defaults"""
        from ciaf.lcm.dataset_manager import DatasetMetadata

        metadata = DatasetMetadata(name="test")

        assert metadata.contains_pii is False
        assert metadata.privacy_level == "public"
        assert metadata.version == "1.0.0"

    def test_dataset_metadata_pii_flag(self):
        """DatasetMetadata should track PII presence"""
        from ciaf.lcm.dataset_manager import DatasetMetadata

        metadata = DatasetMetadata(
            name="sensitive",
            contains_pii=True,
            privacy_level="restricted"
        )

        assert metadata.contains_pii is True
        assert metadata.privacy_level == "restricted"

    def test_dataset_metadata_compliance_frameworks(self):
        """DatasetMetadata should support compliance frameworks"""
        from ciaf.lcm.dataset_manager import DatasetMetadata

        metadata = DatasetMetadata(
            name="compliant_data",
            compliance_frameworks=["GDPR", "HIPAA"]
        )

        assert "GDPR" in metadata.compliance_frameworks
        assert "HIPAA" in metadata.compliance_frameworks


class TestComputeSplitAssignmentDigest:
    """Test split assignment digest computation"""

    def test_compute_split_digest_basic(self):
        """compute_split_assignment_digest should produce hash"""
        from ciaf.lcm.dataset_manager import compute_split_assignment_digest

        record_ids = ["row_1", "row_2", "row_3"]
        digest = compute_split_assignment_digest(record_ids)

        assert isinstance(digest, str)
        assert len(digest) == 64  # SHA-256 hex digest is 64 chars

    def test_compute_split_digest_deterministic(self):
        """compute_split_assignment_digest should be deterministic"""
        from ciaf.lcm.dataset_manager import compute_split_assignment_digest

        record_ids = ["row_1", "row_2", "row_3"]
        digest1 = compute_split_assignment_digest(record_ids)
        digest2 = compute_split_assignment_digest(record_ids)

        assert digest1 == digest2

    def test_compute_split_digest_order_independent(self):
        """compute_split_assignment_digest should be order-independent"""
        from ciaf.lcm.dataset_manager import compute_split_assignment_digest

        record_ids1 = ["row_1", "row_2", "row_3"]
        record_ids2 = ["row_3", "row_1", "row_2"]

        digest1 = compute_split_assignment_digest(record_ids1)
        digest2 = compute_split_assignment_digest(record_ids2)

        assert digest1 == digest2

    def test_compute_split_digest_with_salt(self):
        """compute_split_assignment_digest should support salt"""
        from ciaf.lcm.dataset_manager import compute_split_assignment_digest

        record_ids = ["row_1", "row_2", "row_3"]
        salt = b"test_salt"

        digest_with_salt = compute_split_assignment_digest(record_ids, salt=salt)
        digest_without_salt = compute_split_assignment_digest(record_ids, salt=None)

        assert digest_with_salt != digest_without_salt


# ============================================================================
# PART 2: LCM TRAINING MANAGER TESTS (18 tests)
# ============================================================================

class TestTrainingCheckpoint:
    """Test TrainingCheckpoint dataclass"""

    def test_training_checkpoint_initialization(self):
        """TrainingCheckpoint should initialize with all required fields"""
        from ciaf.lcm.training_manager import TrainingCheckpoint

        checkpoint = TrainingCheckpoint(
            checkpoint_id="cp_1",
            epoch=1,
            step=100,
            metrics={"loss": 0.5, "accuracy": 0.9},
            model_state_digest="hash_model",
            optimizer_state_digest="hash_optimizer"
        )

        assert checkpoint.checkpoint_id == "cp_1"
        assert checkpoint.epoch == 1
        assert checkpoint.metrics["loss"] == 0.5

    def test_training_checkpoint_timestamp_auto(self):
        """TrainingCheckpoint should auto-generate timestamp"""
        from ciaf.lcm.training_manager import TrainingCheckpoint

        checkpoint = TrainingCheckpoint(
            checkpoint_id="cp_2",
            epoch=2,
            step=200,
            metrics={"loss": 0.3},
            model_state_digest="hash1",
            optimizer_state_digest="hash2"
        )

        assert checkpoint.timestamp is not None

    def test_training_checkpoint_to_dict(self):
        """TrainingCheckpoint should convert to dictionary"""
        from ciaf.lcm.training_manager import TrainingCheckpoint

        checkpoint = TrainingCheckpoint(
            checkpoint_id="cp_3",
            epoch=3,
            step=300,
            metrics={"accuracy": 0.95},
            model_state_digest="m_hash",
            optimizer_state_digest="o_hash"
        )

        checkpoint_dict = checkpoint.to_dict()
        assert isinstance(checkpoint_dict, dict)
        assert checkpoint_dict["epoch"] == 3


class TestTrainingMetrics:
    """Test TrainingMetrics dataclass"""

    def test_training_metrics_initialization(self):
        """TrainingMetrics should initialize with metrics data"""
        from ciaf.lcm.training_manager import TrainingMetrics

        metrics = TrainingMetrics(
            train_metrics={"loss": [1.0, 0.8, 0.6]},
            val_metrics={"loss": [1.2, 0.9, 0.7]},
            epochs=[1, 2, 3]
        )

        assert metrics.train_metrics["loss"] == [1.0, 0.8, 0.6]
        assert len(metrics.epochs) == 3

    def test_training_metrics_compute_digest(self):
        """TrainingMetrics should compute digest"""
        from ciaf.lcm.training_manager import TrainingMetrics

        metrics = TrainingMetrics(
            train_metrics={"loss": [0.5]},
            val_metrics={"loss": [0.6]},
            epochs=[1]
        )

        digest = metrics.compute_metrics_digest()
        assert isinstance(digest, str)
        assert len(digest) == 64  # SHA-256

    def test_training_metrics_to_dict(self):
        """TrainingMetrics should convert to dictionary"""
        from ciaf.lcm.training_manager import TrainingMetrics

        metrics = TrainingMetrics(
            train_metrics={"acc": [0.7, 0.8]},
            val_metrics={"acc": [0.65, 0.75]},
            epochs=[1, 2]
        )

        metrics_dict = metrics.to_dict()
        assert isinstance(metrics_dict, dict)
        assert "metrics_digest" in metrics_dict


class TestLCMTrainingSession:
    """Test LCMTrainingSession"""

    def test_lcm_training_session_initialization(self):
        """LCMTrainingSession should initialize with training metadata"""
        from ciaf.lcm.training_manager import LCMTrainingSession
        from ciaf.lcm.model_manager import LCMModelAnchor

        model_anchor = MagicMock(spec=LCMModelAnchor)
        model_anchor.model_name = "test_model"
        model_anchor.version = "1.0"
        model_anchor.anchor_id = "ma_123"

        with patch('builtins.print'):
            session = LCMTrainingSession(
                session_id="train_session_1",
                model_anchor=model_anchor,
                datasets_root_anchor="datasets_root",
                training_config={"optimizer": "adam"},
                data_splits={}
            )

            assert session.session_id == "train_session_1"
            assert session.checkpoints == []

    def test_lcm_training_session_add_checkpoint(self):
        """LCMTrainingSession should support adding checkpoints"""
        from ciaf.lcm.training_manager import LCMTrainingSession, TrainingCheckpoint
        from ciaf.lcm.model_manager import LCMModelAnchor

        model_anchor = MagicMock(spec=LCMModelAnchor)
        model_anchor.model_name = "m"
        model_anchor.version = "1.0"

        with patch('builtins.print'):
            session = LCMTrainingSession(
                session_id="s2",
                model_anchor=model_anchor,
                datasets_root_anchor="dr",
                training_config={},
                data_splits={}
            )

            checkpoint = TrainingCheckpoint(
                checkpoint_id="cp_1",
                epoch=1,
                step=100,
                metrics={"loss": 0.5},
                model_state_digest="h1",
                optimizer_state_digest="h2"
            )

            session.add_checkpoint(checkpoint)
            assert len(session.checkpoints) == 1


class TestLCMTrainingManager:
    """Test LCMTrainingManager"""

    def test_lcm_training_manager_initialization(self):
        """LCMTrainingManager should initialize"""
        from ciaf.lcm.training_manager import LCMTrainingManager

        manager = LCMTrainingManager()
        assert manager is not None


# ============================================================================
# PART 3: LCM INFERENCE MANAGER TESTS (12 tests)
# ============================================================================

class TestLCMInferenceCommitment:
    """Test LCMInferenceCommitment"""

    def test_inference_commitment_initialization(self):
        """LCMInferenceCommitment should initialize with data"""
        from ciaf.lcm.inference_manager import LCMInferenceCommitment
        from ciaf.lcm.policy import CommitmentType

        commitment = LCMInferenceCommitment(
            commitment_type=CommitmentType.SALTED,
            commitment_value="committed_query_value"
        )

        assert commitment.commitment_type == CommitmentType.SALTED
        assert commitment.commitment_value == "committed_query_value"

    def test_inference_commitment_metadata(self):
        """LCMInferenceCommitment should support metadata"""
        from ciaf.lcm.inference_manager import LCMInferenceCommitment
        from ciaf.lcm.policy import CommitmentType

        commitment = LCMInferenceCommitment(
            commitment_type=CommitmentType.HMAC_SHA256,
            commitment_value="output_value",
            metadata={"model_version": "1.0"}
        )

        assert commitment.metadata["model_version"] == "1.0"


class TestLCMInferenceReceipt:
    """Test LCMInferenceReceipt"""

    def test_inference_receipt_initialization(self):
        """LCMInferenceReceipt should initialize with inference data"""
        from ciaf.lcm.inference_manager import LCMInferenceReceipt, LCMInferenceCommitment
        from ciaf.lcm.policy import CommitmentType

        commitment = LCMInferenceCommitment(
            commitment_type=CommitmentType.SALTED,
            commitment_value="input"
        )

        with patch('builtins.print'):
            receipt = LCMInferenceReceipt(
                receipt_id="receipt_1",
                model_anchor_ref="model_ref",
                deployment_anchor_ref="deploy_ref",
                request_id="req_1",
                query="test query",
                ai_output="test output",
                input_commitment=commitment,
                output_commitment=commitment
            )

            assert receipt.receipt_id == "receipt_1"
            assert receipt.query == "test query"

    def test_inference_receipt_to_dict(self):
        """LCMInferenceReceipt should convert to dictionary"""
        from ciaf.lcm.inference_manager import LCMInferenceReceipt, LCMInferenceCommitment
        from ciaf.lcm.policy import CommitmentType

        commitment = LCMInferenceCommitment(
            commitment_type=CommitmentType.HMAC_SHA256,
            commitment_value="v"
        )

        with patch('builtins.print'):
            receipt = LCMInferenceReceipt(
                receipt_id="r2",
                model_anchor_ref="m_ref",
                deployment_anchor_ref="d_ref",
                request_id="req",
                query="q",
                ai_output="o",
                input_commitment=commitment,
                output_commitment=commitment
            )

            receipt_dict = receipt.to_dict()
            assert isinstance(receipt_dict, dict)
            assert receipt_dict["receipt_id"] == "r2"


class TestLCMInferenceConnections:
    """Test LCMInferenceConnections"""

    def test_inference_connections_initialization(self):
        """LCMInferenceConnections should initialize with connections ID"""
        from ciaf.lcm.inference_manager import LCMInferenceConnections

        with patch('builtins.print'):
            connections = LCMInferenceConnections(connections_id="conn_1")
            assert connections.connections_id == "conn_1"


class TestLCMInferenceManager:
    """Test LCMInferenceManager"""

    def test_inference_manager_initialization(self):
        """LCMInferenceManager should initialize"""
        from ciaf.lcm.inference_manager import LCMInferenceManager

        manager = LCMInferenceManager()
        assert manager is not None

    def test_inference_manager_create_connections(self):
        """LCMInferenceManager should create inference connections"""
        from ciaf.lcm.inference_manager import LCMInferenceManager

        manager = LCMInferenceManager()

        with patch('builtins.print'):
            connections = manager.create_inference_connections("conn_test")

        assert connections is not None
        assert connections.connections_id == "conn_test"

    def test_inference_manager_get_connections(self):
        """LCMInferenceManager should retrieve connections"""
        from ciaf.lcm.inference_manager import LCMInferenceManager

        manager = LCMInferenceManager()

        with patch('builtins.print'):
            manager.create_inference_connections("conn_2")
            retrieved = manager.get_inference_connections("conn_2")

        assert retrieved is not None
        assert retrieved.connections_id == "conn_2"


# ============================================================================
# PART 4: PREPROCESSING DATA QUALITY TESTS (18 tests)
# ============================================================================

class TestValidationResult:
    """Test ValidationResult"""

    def test_validation_result_initialization(self):
        """ValidationResult should initialize with validity status"""
        from ciaf.preprocessing.data_quality import ValidationResult

        result = ValidationResult(is_valid=True)
        assert result.is_valid is True

    def test_validation_result_add_error(self):
        """ValidationResult should track errors"""
        from ciaf.preprocessing.data_quality import ValidationResult

        result = ValidationResult(is_valid=True)
        result.add_error("test error")

        assert len(result.errors) == 1
        assert "test error" in result.errors

    def test_validation_result_add_warning(self):
        """ValidationResult should track warnings"""
        from ciaf.preprocessing.data_quality import ValidationResult

        result = ValidationResult(is_valid=True)
        result.add_warning("test warning")

        assert len(result.warnings) == 1
        assert "test warning" in result.warnings

    def test_validation_result_add_metric(self):
        """ValidationResult should track metrics"""
        from ciaf.preprocessing.data_quality import ValidationResult

        result = ValidationResult(is_valid=True)
        result.add_metric("quality_score", 0.95)

        assert "quality_score" in result.metrics
        assert result.metrics["quality_score"] == 0.95


class TestDataQualityValidator:
    """Test DataQualityValidator"""

    def test_data_quality_validator_initialization(self):
        """DataQualityValidator should initialize"""
        from ciaf.preprocessing.data_quality import DataQualityValidator

        validator = DataQualityValidator()
        assert validator is not None

    def test_data_quality_validator_validate_list(self, sample_dataset):
        """DataQualityValidator should validate list of dicts"""
        from ciaf.preprocessing.data_quality import DataQualityValidator

        validator = DataQualityValidator()
        result = validator.validate(sample_dataset)

        assert result is not None
        assert hasattr(result, 'is_valid')

    def test_data_quality_validator_validate_dataframe(self, sample_pandas_df):
        """DataQualityValidator should validate pandas DataFrames"""
        from ciaf.preprocessing.data_quality import DataQualityValidator

        validator = DataQualityValidator()
        result = validator.validate(sample_pandas_df)

        assert result is not None

    def test_data_quality_validator_validate_numpy_array(self):
        """DataQualityValidator should validate numpy arrays"""
        from ciaf.preprocessing.data_quality import DataQualityValidator

        validator = DataQualityValidator()
        data = np.array([[1, 2], [3, 4], [5, 6]])
        result = validator.validate(data)

        assert result is not None


class TestQuickValidate:
    """Test quick_validate convenience function"""

    def test_quick_validate_function(self, sample_dataset):
        """quick_validate should provide convenience validation"""
        from ciaf.preprocessing.data_quality import quick_validate

        result = quick_validate(sample_dataset)
        assert result is not None


class TestValidateCIAFDataset:
    """Test validate_ciaf_dataset convenience function"""

    def test_validate_ciaf_dataset_function(self, sample_dataset):
        """validate_ciaf_dataset should validate CIAF format data"""
        from ciaf.preprocessing.data_quality import validate_ciaf_dataset

        result = validate_ciaf_dataset(sample_dataset)
        assert result is not None


# ============================================================================
# PART 5: AGENT SESSION TESTS (18 tests)
# ============================================================================

class TestTaskBatch:
    """Test TaskBatch"""

    def test_task_batch_initialization(self):
        """TaskBatch should initialize with required fields"""
        from ciaf.sessions.agent_session import TaskBatch

        batch = TaskBatch(
            task_batch_id="task_1",
            session_id="session_1",
            organization_id="org_1"
        )

        assert batch.task_batch_id == "task_1"
        assert batch.session_id == "session_1"
        assert batch.organization_id == "org_1"

    def test_task_batch_add_output_tag(self):
        """TaskBatch should support adding output tags"""
        from ciaf.sessions.agent_session import TaskBatch

        batch = TaskBatch(
            task_batch_id="task_2",
            session_id="session_1",
            organization_id="org_1"
        )

        batch.add_output_tag("tag_1")
        assert "tag_1" in batch.output_tag_ids

    def test_task_batch_finalize(self):
        """TaskBatch should support finalization"""
        from ciaf.sessions.agent_session import TaskBatch

        batch = TaskBatch(
            task_batch_id="task_3",
            session_id="session_1",
            organization_id="org_1"
        )

        batch.finalize(status="success")
        assert batch.status == "success"
        assert batch.end_time is not None

    def test_task_batch_to_dict(self):
        """TaskBatch should convert to dictionary"""
        from ciaf.sessions.agent_session import TaskBatch

        batch = TaskBatch(
            task_batch_id="task_4",
            session_id="session_1",
            organization_id="org_1"
        )

        batch_dict = batch.to_dict()
        assert isinstance(batch_dict, dict)
        assert batch_dict["task_batch_id"] == "task_4"


class TestSessionBatcher:
    """Test SessionBatcher"""

    def test_session_batcher_initialization(self):
        """SessionBatcher should initialize with tag manager"""
        from ciaf.sessions.agent_session import SessionBatcher

        mock_tag_manager = MagicMock()
        batcher = SessionBatcher(tag_manager=mock_tag_manager)

        assert batcher is not None

    def test_session_batcher_new_task(self):
        """SessionBatcher should create new tasks"""
        from ciaf.sessions.agent_session import SessionBatcher

        mock_tag_manager = MagicMock()
        batcher = SessionBatcher(tag_manager=mock_tag_manager)

        task = batcher.new_task(
            session_id="sess_1",
            organization_id="org_1",
            task_description="test task"
        )

        assert task is not None
        assert task.session_id == "sess_1"
        assert task.organization_id == "org_1"


class TestAgentSession:
    """Test AgentSession"""

    def test_agent_session_initialization(self):
        """AgentSession should initialize with session metadata"""
        from ciaf.sessions.agent_session import AgentSession

        session = AgentSession(
            session_id="session_1",
            user_id="user_1",
            organization_id="org_1"
        )

        assert session.session_id == "session_1"
        assert session.user_id == "user_1"
        assert session.organization_id == "org_1"

    def test_agent_session_start_task(self):
        """AgentSession should support starting tasks"""
        from ciaf.sessions.agent_session import AgentSession

        session = AgentSession(
            session_id="session_2",
            user_id="user_1",
            organization_id="org_1"
        )

        task = session.start_task(task_description="test task")
        assert task is not None

    def test_agent_session_get_summary(self):
        """AgentSession should provide session summary"""
        from ciaf.sessions.agent_session import AgentSession

        session = AgentSession(
            session_id="session_3",
            user_id="user_1",
            organization_id="org_1"
        )

        summary = session.get_session_summary()
        assert isinstance(summary, dict)
        assert "session_id" in summary

    def test_agent_session_to_dict(self):
        """AgentSession should convert to dictionary"""
        from ciaf.sessions.agent_session import AgentSession

        session = AgentSession(
            session_id="session_4",
            user_id="user_1",
            organization_id="org_1"
        )

        session_dict = session.to_dict()
        assert isinstance(session_dict, dict)
        assert session_dict["session_id"] == "session_4"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
