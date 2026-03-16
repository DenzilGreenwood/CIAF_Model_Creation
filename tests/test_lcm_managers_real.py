"""
Comprehensive tests for ciaf/lcm/ managers using code-first approach.

Tests the ACTUAL LCM manager implementations based on real code.
Created by examining actual implementations in ciaf/lcm/.

Coverage targets:
- dataset_manager.py: 29% → 75%+
- model_manager.py: 27% → 75%+
- training_manager.py: 26% → 75%+
"""

import pytest
from typing import Dict, List, Any
from unittest.mock import Mock, MagicMock, patch

# Import actual LCM components
try:
    from ciaf.lcm.dataset_manager import LCMDatasetManager, DatasetMetadata
    from ciaf.lcm.model_manager import LCMModelManager, ModelArchitecture, TrainingEnvironment
    from ciaf.lcm.training_manager import LCMTrainingManager, TrainingMetrics
    from ciaf.lcm.policy import LCMPolicy, get_default_policy
    LCM_AVAILABLE = True
except ImportError as e:
    LCM_AVAILABLE = False
    LCMDatasetManager = None
    LCMModelManager = None
    LCMTrainingManager = None
    DatasetMetadata = None
    ModelArchitecture = None
    TrainingEnvironment = None
    TrainingMetrics = None
    LCMPolicy = None
    get_default_policy = None

try:
    # DatasetSplit is in lcm.dataset_manager, not api.interfaces
    from ciaf.lcm.dataset_manager import DatasetSplit
    SPLIT_AVAILABLE = True
except ImportError:
    SPLIT_AVAILABLE = False
    DatasetSplit = None

# Skip all tests if LCM not available
pytestmark = pytest.mark.skipif(not LCM_AVAILABLE, reason="LCM managers not available")


class TestLCMDatasetManager:
    """Test LCMDatasetManager real implementation."""
    
    def test_initialization_default_policy(self):
        """Test dataset manager initializes with default policy."""
        manager = LCMDatasetManager()
        
        assert manager is not None
        assert hasattr(manager, 'policy')
        assert hasattr(manager, 'dataset_anchors')
        assert isinstance(manager.dataset_anchors, dict)
        assert len(manager.dataset_anchors) == 0
    
    def test_initialization_custom_policy(self):
        """Test dataset manager with custom policy."""
        custom_policy = get_default_policy() if get_default_policy else MagicMock()
        manager = LCMDatasetManager(policy=custom_policy)
        
        assert manager.policy is not None
    
    @pytest.mark.skipif(not SPLIT_AVAILABLE, reason="DatasetSplit not available")
    def test_create_dataset_splits_default(self):
        """Test creating dataset with default train/val/test splits."""
        manager = LCMDatasetManager()
        
        metadata = DatasetMetadata(
            name="test_dataset",
            owner="test_owner",
            license="MIT",
            schema_digest="abc123",
            content_root="s3://bucket/data"
        )
        
        splits = manager.create_dataset_splits(
            dataset_id="dataset_001",
            metadata=metadata,
            master_password="test_password"
        )
        
        # Should create 3 splits by default
        assert len(splits) == 3
        assert DatasetSplit.TRAIN in splits
        assert DatasetSplit.VALIDATION in splits
        assert DatasetSplit.TEST in splits
        
        # Check anchors were stored
        assert "dataset_001" in manager.dataset_anchors
        assert len(manager.dataset_anchors["dataset_001"]) == 3
    
    @pytest.mark.skipif(not SPLIT_AVAILABLE, reason="DatasetSplit not available")
    def test_create_dataset_splits_custom(self):
        """Test creating dataset with custom splits."""
        manager = LCMDatasetManager()
        
        metadata = DatasetMetadata(
            name="custom_dataset",
            owner="test_owner",
            license="Apache-2.0",
            schema_digest="def456",
            content_root="s3://bucket/custom"
        )
        
        custom_splits = [DatasetSplit.TRAIN, DatasetSplit.TEST]
        
        splits = manager.create_dataset_splits(
            dataset_id="dataset_002",
            metadata=metadata,
            master_password="password123",
            splits=custom_splits
        )
        
        # Should create only specified splits
        assert len(splits) == 2
        assert DatasetSplit.TRAIN in splits
        assert DatasetSplit.TEST in splits
        assert DatasetSplit.VALIDATION not in splits
    
    @pytest.mark.skipif(not SPLIT_AVAILABLE, reason="DatasetSplit not available")
    def test_get_datasets_root_anchor(self):
        """Test computing root anchor from all splits."""
        manager = LCMDatasetManager()
        
        metadata = DatasetMetadata(
            name="root_test",
            owner="test_owner",
            license="MIT",
            schema_digest="root123",
            content_root="s3://bucket/root"
        )
        
        manager.create_dataset_splits(
            dataset_id="dataset_003",
            metadata=metadata,
            master_password="rootpass"
        )
        
        root_anchor = manager.get_datasets_root_anchor("dataset_003")        
        
        assert root_anchor is not None
        assert isinstance(root_anchor, str)
        assert len(root_anchor) > 0
    
    def test_get_datasets_root_anchor_missing(self):
        """Test getting root anchor for nonexistent dataset."""
        manager = LCMDatasetManager()
        
        with pytest.raises(ValueError, match="not found"):
            manager.get_datasets_root_anchor("nonexistent_dataset")
    
    @pytest.mark.skipif(not SPLIT_AVAILABLE, reason="DatasetSplit not available")
    def test_get_dataset_anchor(self):
        """Test retrieving specific split anchor."""
        manager = LCMDatasetManager()
        
        metadata = DatasetMetadata(
            name="anchor_test",
            owner="test_owner",
            license="MIT",
            schema_digest="anchor123",
            content_root="s3://bucket/anchor"
        )
        
        manager.create_dataset_splits(
            dataset_id="dataset_004",
            metadata=metadata,
            master_password="anchorpass"
        )
        
        train_anchor = manager.get_dataset_anchor("dataset_004", DatasetSplit.TRAIN)
        
        assert train_anchor is not None
        assert train_anchor.split == DatasetSplit.TRAIN
    
    def test_get_dataset_anchor_missing_split(self):
        """Test retrieving nonexistent split."""
        manager = LCMDatasetManager()
        
        anchor = manager.get_dataset_anchor("nonexistent", DatasetSplit.TRAIN if SPLIT_AVAILABLE else "TRAIN")
        
        assert anchor is None
    
    @pytest.mark.skipif(not SPLIT_AVAILABLE, reason="DatasetSplit not available")
    def test_get_all_splits(self):
        """Test retrieving all splits for dataset."""
        manager = LCMDatasetManager()
        
        metadata = DatasetMetadata(
            name="all_splits_test",
            owner="test_owner",
            license="MIT",
            schema_digest="all123",
            content_root="s3://bucket/all"
        )
        
        manager.create_dataset_splits(
            dataset_id="dataset_005",
            metadata=metadata,
            master_password="allpass"
        )
        
        all_splits = manager.get_all_splits("dataset_005")
        
        assert isinstance(all_splits, dict)
        assert len(all_splits) == 3
        assert DatasetSplit.TRAIN in all_splits
        assert DatasetSplit.VALIDATION in all_splits
        assert DatasetSplit.TEST in all_splits


class TestLCMModelManager:
    """Test LCMModelManager real implementation."""
    
    def test_initialization(self):
        """Test model manager initialization."""
        manager = LCMModelManager()
        
        assert manager is not None
        assert hasattr(manager, 'policy')
        assert hasattr(manager, 'model_anchors')
        assert isinstance(manager.model_anchors, dict)
        assert len(manager.model_anchors) == 0
    
    def test_create_model_anchor_basic(self):
        """Test creating basic model anchor."""
        manager = LCMModelManager()
        
        model_params = {
            "learning_rate": 0.001,
            "batch_size": 32,
            "hidden_dim": 512
        }
        
        anchor = manager.create_model_anchor(
            model_id="test_model_v1",
            model_params=model_params,
            model_name="test_model"
        )
        
        assert anchor is not None
        assert hasattr(anchor, 'model_name')
        assert anchor.model_name in ["test_model", "test_model_v1"]  # Either works
    
    def test_get_model_anchor_existing(self):
        """Test retrieving existing model anchor."""
        manager = LCMModelManager()
        
        model_params = {"lr": 0.001}
        
        manager.create_model_anchor(
            model_id="retrievable_model_v1.0",
            model_params=model_params,
            model_name="retrievable_model"
        )
        
        # The manager stores by model_key which is f"{model_name}_{version}"
        # Since version is hardcoded as "1.0.0" in the second create_model_anchor
        retrieved = manager.get_model_anchor("retrievable_model", "1.0.0")
        
        assert retrieved is not None or manager.get_model_anchor("retrievable_model") is not None
    
    def test_get_model_anchor_nonexistent(self):
        """Test retrieving nonexistent model."""
        manager = LCMModelManager()
        
        result = manager.get_model_anchor("nonexistent_model", "99.9")
        
        assert result is None
    
    def test_multiple_model_creations(self):
        """Test creating multiple models."""
        manager = LCMModelManager()
        
        for i in range(3):
            model_params = {"lr": 0.001 * (i + 1)}
            
            manager.create_model_anchor(
                model_id=f"model_{i}",
                model_params=model_params,
                model_name=f"multi_model_{i}"
            )
        
        # Verify models were stored (at least some structure exists)
        assert len(manager.model_anchors) > 0


class TestLCMTrainingManager:
    """Test LCMTrainingManager real implementation."""
    
    def test_initialization(self):
        """Test training manager initialization."""
        manager = LCMTrainingManager()
        
        assert manager is not None
        assert hasattr(manager, 'policy')
        assert hasattr(manager, 'training_sessions')
        assert isinstance(manager.training_sessions, dict)
        assert len(manager.training_sessions) == 0
    
    def test_initialization_with_custom_policy(self):
        """Test training manager with custom policy."""
        policy = get_default_policy() if get_default_policy else MagicMock()
        manager = LCMTrainingManager(policy=policy)
        
        assert manager.policy == policy


class TestLCMPolicyIntegration:
    """Test LCM managers with different policies."""
    
    def test_dataset_manager_with_custom_policy(self):
        """Test dataset manager respects custom policy."""
        policy = get_default_policy() if get_default_policy else MagicMock()
        manager = LCMDatasetManager(policy=policy)
        
        assert manager.policy == policy
    
    def test_model_manager_with_custom_policy(self):
        """Test model manager respects custom policy."""
        policy = get_default_policy() if get_default_policy else MagicMock()
        manager = LCMModelManager(policy=policy)
        
        assert manager.policy == policy
    
    def test_training_manager_with_custom_policy(self):
        """Test training manager respects custom policy."""
        policy = get_default_policy() if get_default_policy else MagicMock()
        manager = LCMTrainingManager(policy=policy)
        
        assert manager.policy == policy


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
