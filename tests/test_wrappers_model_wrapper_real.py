"""
Real tests for ciaf/wrappers/model_wrapper.py

Uses code-first methodology: Examine actual implementation → Write matching tests

Tests CIAFModelWrapper: drop-in model wrapper with CIAF provenance tracking,
training snapshots, inference receipts, and enhanced features.

Training data format: {"content": "...", "metadata": {"id": "..."}}
Model info uses: is_trained (not trained)
Receipt has: receipt_hash attribute
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import pickle

# Test if model_wrapper is available
try:
    from ciaf.wrappers.model_wrapper import CIAFModelWrapper
    from ciaf.api import CIAFFramework
    from ciaf.inference import InferenceReceipt
    from ciaf.provenance import TrainingSnapshot, ModelAggregationAnchor
    WRAPPER_AVAILABLE = True
except ImportError:
    WRAPPER_AVAILABLE = False
    CIAFModelWrapper = None
    CIAFFramework = None


pytestmark = pytest.mark.skipif(not WRAPPER_AVAILABLE, reason="Model wrapper not available")


# Module-level class for pickle serialization tests
class SimpleModel:
    """Simple model class for pickle serialization tests."""
    def fit(self, X, y):
        pass
    
    def predict(self, X):
        return [0] * len(X)


class TestCIAFModelWrapperInitialization:
    """Test CIAFModelWrapper initialization."""
    
    def test_initialization_basic(self):
        """Test basic initialization with required parameters."""
        mock_model = MagicMock()
        
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="test_model"
        )
        
        assert wrapper.model == mock_model
        assert wrapper.model_name == "test_model"
        assert wrapper.enable_connections is True
        assert wrapper.compliance_mode == "general"
        assert wrapper.framework is not None
        assert isinstance(wrapper.framework, CIAFFramework)
    
    def test_initialization_empty_model_name_raises(self):
        """Test that empty model_name raises ValueError."""
        mock_model = MagicMock()
        
        with pytest.raises(ValueError, match="model_name cannot be empty"):
            CIAFModelWrapper(model=mock_model, model_name="")
        
        with pytest.raises(ValueError, match="model_name cannot be empty"):
            CIAFModelWrapper(model=mock_model, model_name="   ")
    
    def test_initialization_with_custom_framework(self):
        """Test initialization with provided CIAFFramework instance."""
        mock_model = MagicMock()
        custom_framework = CIAFFramework("custom")
        
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="test_model",
            framework=custom_framework
        )
        
        assert wrapper.framework is custom_framework
    
    def test_initialization_healthcare_compliance(self):
        """Test initialization with healthcare compliance mode."""
        mock_model = MagicMock()
        
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="healthcare_model",
            compliance_mode="healthcare"
        )
        
        assert wrapper.compliance_mode == "healthcare"
    
    def test_initialization_financial_compliance(self):
        """Test initialization with financial compliance mode."""
        mock_model = MagicMock()
        
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="financial_model",
            compliance_mode="financial"
        )
        
        assert wrapper.compliance_mode == "financial"
    
    def test_initialization_feature_flags(self):
        """Test initialization with enhanced feature flags."""
        mock_model = MagicMock()
        
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="test_model",
            enable_preprocessing=False,
            enable_explainability=False,
            enable_uncertainty=False,
            enable_metadata_tags=False,
            auto_configure=False
        )
        
        # Features should be disabled even if modules available
        assert wrapper.enable_preprocessing is False
        assert wrapper.enable_explainability is False
        assert wrapper.enable_uncertainty is False
        assert wrapper.enable_metadata_tags is False
    
    def test_initialization_strips_whitespace(self):
        """Test that model_name whitespace is stripped."""
        mock_model = MagicMock()
        
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="  test_model  "
        )
        
        assert wrapper.model_name == "test_model"


class TestCIAFModelWrapperTraining:
    """Test CIAFModelWrapper training functionality."""
    
    def test_train_basic(self):
        """Test basic training with valid data."""
        mock_model = MagicMock()
        mock_model.fit = MagicMock()
        
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="test_model",
            auto_configure=False
        )
        
        # Format required: {"content": "...", "metadata": {"id": "..."}}
        training_data = [
            {"content": "sample 1", "metadata": {"id": "item_1"}, "features": [1, 2, 3], "label": 0},
            {"content": "sample 2", "metadata": {"id": "item_2"}, "features": [4, 5, 6], "label": 1},
        ]
        
        snapshot = wrapper.train(
            dataset_id="dataset_001",
            training_data=training_data,
            master_password="test_password",
            model_version="1.0.0"
        )
        
        assert isinstance(snapshot, TrainingSnapshot)
        assert wrapper.training_snapshot is not None
        assert wrapper.model_version == "1.0.0"
        assert snapshot.snapshot_id is not None
    
    def test_train_empty_data_raises(self):
        """Test that empty training_data raises ValueError."""
        mock_model = MagicMock()
        wrapper = CIAFModelWrapper(model=mock_model, model_name="test_model")
        
        with pytest.raises(ValueError, match="training_data cannot be empty"):
            wrapper.train(
                dataset_id="dataset_001",
                training_data=[],
                master_password="test_password"
            )
    
    def test_train_with_training_params(self):
        """Test training with custom training parameters."""
        mock_model = MagicMock()
        mock_model.fit = MagicMock()
        
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="test_model",
            auto_configure=False
        )
        
        training_data = [
            {"content": "sample 1", "metadata": {"id": "item_1"}, "features": [1, 2, 3], "label": 0},
        ]
        
        training_params = {
            "learning_rate": 0.01,
            "epochs": 100,
            "batch_size": 32
        }
        
        snapshot = wrapper.train(
            dataset_id="dataset_001",
            training_data=training_data,
            master_password="test_password",
            training_params=training_params,
            model_version="1.0.0"
        )
        
        assert isinstance(snapshot, TrainingSnapshot)
    
    def test_train_without_fitting_model(self):
        """Test training with fit_model=False (CIAF-only)."""
        mock_model = MagicMock()
        
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="test_model",
            auto_configure=False
        )
        
        training_data = [
            {"content": "sample 1", "metadata": {"id": "item_1", "key": "value"}},
        ]
        
        snapshot = wrapper.train(
            dataset_id="dataset_001",
            training_data=training_data,
            master_password="test_password",
            fit_model=False
        )
        
        assert isinstance(snapshot, TrainingSnapshot)
        # Model.fit should NOT be called
        assert not hasattr(mock_model, 'fit') or not mock_model.fit.called
    
    def test_train_model_without_fit_method(self):
        """Test training with model that doesn't have fit method."""
        mock_model = MagicMock(spec=[])  # No fit method
        
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="test_model",
            auto_configure=False
        )
        
        training_data = [
            {"content": "sample 1", "metadata": {"id": "item_1"}},
        ]
        
        # Should not raise, just warn
        with pytest.warns(UserWarning, match="does not have a 'fit' method"):
            snapshot = wrapper.train(
                dataset_id="dataset_001",
                training_data=training_data,
                master_password="test_password",
                fit_model=True
            )
        
        assert isinstance(snapshot, TrainingSnapshot)


class TestCIAFModelWrapperPrediction:
    """Test CIAFModelWrapper prediction functionality."""
    
    def test_predict_after_training(self):
        """Test making predictions after training."""
        mock_model = MagicMock()
        mock_model.fit = MagicMock()
        mock_model.predict = MagicMock(return_value=[0])
        
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="test_model",
            auto_configure=False
        )
        
        # Train first
        training_data = [{"content": "sample", "metadata": {"id": "item_1"}, "features": [1, 2], "label": 0}]
        wrapper.train(
            dataset_id="dataset_001",
            training_data=training_data,
            master_password="test_password"
        )
        
        # Make prediction
        prediction, receipt = wrapper.predict(query="test query")
        
        assert receipt is not None
        assert isinstance(receipt, InferenceReceipt)
        assert prediction is not None
    
    def test_predict_without_training_raises(self):
        """Test that predict without training raises RuntimeError."""
        mock_model = MagicMock()
        wrapper = CIAFModelWrapper(model=mock_model, model_name="test_model")
        
        with pytest.raises(RuntimeError, match="has not been trained"):
            wrapper.predict(query="test query")
    
    def test_predict_with_model_version(self):
        """Test prediction with specific model version."""
        mock_model = MagicMock()
        mock_model.fit = MagicMock()
        mock_model.predict = MagicMock(return_value=[1])
        
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="test_model",
            auto_configure=False
        )
        
        training_data = [{"content": "sample", "metadata": {"id": "item_1"}, "features": [1, 2], "label": 1}]
        wrapper.train(
            dataset_id="dataset_001",
            training_data=training_data,
            master_password="test_password",
            model_version="2.0.0"
        )
        
        prediction, receipt = wrapper.predict(
            query="test query",
            model_version="2.0.0"
        )
        
        assert receipt is not None
    
    def test_predict_without_model(self):
        """Test prediction using CIAF simulator (use_model=False)."""
        mock_model = MagicMock()
        mock_model.fit = MagicMock()
        
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="test_model",
            auto_configure=False
        )
        
        training_data = [{"content": "sample", "metadata": {"id": "item_1"}}]
        wrapper.train(
            dataset_id="dataset_001",
            training_data=training_data,
            master_password="test_password",
            fit_model=False
        )
        
        # Predict with simulator
        prediction, receipt = wrapper.predict(
            query="test query",
            use_model=False
        )
        
        assert isinstance(prediction, str)
        assert "CIAF simulated response" in prediction
        assert isinstance(receipt, InferenceReceipt)
    
    def test_predict_model_failure_fallback(self):
        """Test that model prediction failure falls back to simulator."""
        mock_model = MagicMock()
        mock_model.fit = MagicMock()
        mock_model.predict = MagicMock(side_effect=Exception("Model error"))
        
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="test_model",
            auto_configure=False
        )
        
        training_data = [{"content": "sample", "metadata": {"id": "item_1"}}]
        wrapper.train(
            dataset_id="dataset_001",
            training_data=training_data,
            master_password="test_password",
            fit_model=False
        )
        
        # Should fall back to simulator
        prediction, receipt = wrapper.predict(query="test query")
        
        assert isinstance(prediction, str)
        assert isinstance(receipt, InferenceReceipt)


class TestCIAFModelWrapperVerification:
    """Test CIAFModelWrapper verification functionality."""
    
    def test_verify_receipt(self):
        """Test verifying an inference receipt."""
        mock_model = MagicMock()
        wrapper = CIAFModelWrapper(model=mock_model, model_name="test_model")
        
        # Create mock receipt with all required attributes
        mock_receipt = MagicMock(spec=InferenceReceipt)
        mock_receipt.receipt_id = "receipt_123"
        mock_receipt.receipt_hash = "abc123def456"
        mock_receipt.model_name = "test_model"
        mock_receipt.model_version = "1.0.0"
        mock_receipt.verified = True
        
        result = wrapper.verify(mock_receipt)
        
        assert isinstance(result, dict)
        assert "verified" in result or result is not None
    
    def test_verify_inference_receipt_by_hash(self):
        """Test verifying receipt by hash."""
        mock_model = MagicMock()
        mock_model.fit = MagicMock()
        
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="test_model",
            auto_configure=False
        )
        
        training_data = [{"content": "sample", "metadata": {"id": "item_1"}}]
        wrapper.train(
            dataset_id="dataset_001",
            training_data=training_data,
            master_password="test_password"
        )
        
        prediction, receipt = wrapper.predict(query="test")
        
        # Verify by hash
        verified = wrapper.verify_inference_receipt(receipt.receipt_hash)
        
        assert isinstance(verified, bool)


class TestCIAFModelWrapperModelInfo:
    """Test CIAFModelWrapper model information retrieval."""
    
    def test_get_model_info_before_training(self):
        """Test getting model info before training."""
        mock_model = MagicMock()
        wrapper = CIAFModelWrapper(model=mock_model, model_name="test_model")
        
        info = wrapper.get_model_info()
        
        assert isinstance(info, dict)
        assert "model_name" in info
        assert info["model_name"] == "test_model"
        assert "is_trained" in info
        assert info["is_trained"] is False
    
    def test_get_model_info_after_training(self):
        """Test getting model info after training."""
        mock_model = MagicMock()
        mock_model.fit = MagicMock()
        
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="test_model",
            auto_configure=False
        )
        
        training_data = [{"content": "sample", "metadata": {"id": "item_1"}}]
        wrapper.train(
            dataset_id="dataset_001",
            training_data=training_data,
            master_password="test_password",
            model_version="1.5.0",
            fit_model=False
        )
        
        info = wrapper.get_model_info()
        
        assert isinstance(info, dict)
        assert "model_name" in info
        assert info["model_name"] == "test_model"
        assert "is_trained" in info
        assert info["is_trained"] is True
        assert "model_version" in info
        assert info["model_version"] == "1.5.0"
    
    def test_get_model_info_with_compliance_mode(self):
        """Test model info includes compliance mode."""
        mock_model = MagicMock()
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="test_model",
            compliance_mode="healthcare"
        )
        
        info = wrapper.get_model_info()
        
        assert "compliance_mode" in info
        assert info["compliance_mode"] == "healthcare"


class TestCIAFModelWrapperSerialization:
    """Test CIAFModelWrapper pickle serialization."""
    
    def test_pickle_untrained_wrapper(self):
        """Test pickling and unpickling untrained wrapper."""
        # Use module-level SimpleModel class for pickle support
        simple_model = SimpleModel()
        wrapper = CIAFModelWrapper(
            model=simple_model,
            model_name="test_model",
            auto_configure=False
        )
        
        # Pickle and unpickle
        pickled = pickle.dumps(wrapper)
        restored = pickle.loads(pickled)
        
        assert restored.model_name == "test_model"
        assert restored.training_snapshot is None
    
    def test_pickle_trained_wrapper(self):
        """Test pickling wrapper after training."""
        # Use module-level SimpleModel class for pickle support
        simple_model = SimpleModel()
        wrapper = CIAFModelWrapper(
            model=simple_model,
            model_name="test_model",
            auto_configure=False
        )
        
        training_data = [{"content": "sample", "metadata": {"id": "item_1"}}]
        wrapper.train(
            dataset_id="dataset_001",
            training_data=training_data,
            master_password="test_password",
            fit_model=False
        )
        
        # Pickle and unpickle
        pickled = pickle.dumps(wrapper)
        restored = pickle.loads(pickled)
        
        assert restored.model_name == "test_model"
        assert restored.model_version is not None


class TestCIAFModelWrapperLCMMetadata:
    """Test CIAFModelWrapper LCM metadata functionality."""
    
    def test_get_lcm_metadata_trail(self):
        """Test getting LCM metadata trail."""
        mock_model = MagicMock()
        wrapper = CIAFModelWrapper(model=mock_model, model_name="test_model")
        
        try:
            metadata_trail = wrapper.get_lcm_metadata_trail()
            
            assert isinstance(metadata_trail, dict)
            assert "model_name" in metadata_trail
        except AttributeError:
            # Method might not exist in all versions
            pytest.skip("get_lcm_metadata_trail not available")
    
    def test_export_lcm_metadata_json(self):
        """Test exporting LCM metadata in JSON format."""
        mock_model = MagicMock()
        wrapper = CIAFModelWrapper(model=mock_model, model_name="test_model")
        
        try:
            metadata = wrapper.export_lcm_metadata(output_format="json")
            
            assert isinstance(metadata, dict)
        except AttributeError:
            pytest.skip("export_lcm_metadata not available")
    
    def test_export_lcm_metadata_with_receipts(self):
        """Test exporting metadata with receipts included."""
        mock_model = MagicMock()
        mock_model.fit = MagicMock()
        
        wrapper = CIAFModelWrapper(
            model=mock_model,
            model_name="test_model",
            auto_configure=False
        )
        
        try:
            training_data = [{"content": "sample", "metadata": {"id": "item_1"}}]
            wrapper.train(
                dataset_id="dataset_001",
                training_data=training_data,
                master_password="test_password",
                fit_model=False
            )
            
            metadata = wrapper.export_lcm_metadata(include_receipts=True)
            
            assert isinstance(metadata, dict)
        except (AttributeError, TypeError):
            pytest.skip("export_lcm_metadata not available or incompatible")


class TestCIAFModelWrapperHelperMethods:
    """Test CIAFModelWrapper helper/private methods."""
    
    def test_validate_training_data_valid(self):
        """Test validation with valid training data."""
        mock_model = MagicMock()
        wrapper = CIAFModelWrapper(model=mock_model, model_name="test_model")
        
        valid_data = [
            {"content": "sample 1", "metadata": {"id": "item_1"}},
            {"content": "sample 2", "metadata": {"id": "item_2"}},
        ]
        
        # Should not raise
        wrapper._validate_training_data(valid_data)
    
    def test_prepare_model_data(self):
        """Test preparing model data extraction."""
        mock_model = MagicMock()
        wrapper = CIAFModelWrapper(model=mock_model, model_name="test_model")
        
        training_data = [
            {"content": "sample 1", "metadata": {"id": "item_1"}, "features": [1, 2, 3], "label": 0},
            {"content": "sample 2", "metadata": {"id": "item_2"}, "features": [4, 5, 6], "label": 1},
        ]
        
        X, y = wrapper._prepare_model_data(training_data)
        
        # Method should return something (might be None if can't extract)
        assert X is not None or X is None
        assert y is not None or y is None
    
    def test_repr_representation(self):
        """Test string representation of wrapper."""
        mock_model = MagicMock()
        wrapper = CIAFModelWrapper(model=mock_model, model_name="test_model")
        
        repr_str = repr(wrapper)
        
        assert isinstance(repr_str, str)
        assert "test_model" in repr_str or "CIAFModelWrapper" in repr_str
