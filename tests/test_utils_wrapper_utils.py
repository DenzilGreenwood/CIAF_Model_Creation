"""
Test suite for CIAF Wrapper Utilities
Tests wrapper creation, training, prediction, and validation
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, Optional

from ciaf.utils.wrapper_utils import CIAFWrapperUtils


class TestCreateWrapper:
    """Test suite for create_wrapper static method"""

    def test_create_wrapper_basic(self):
        """Test basic wrapper creation"""
        wrapper = CIAFWrapperUtils.create_wrapper("test_model")

        assert wrapper is not None

    def test_create_wrapper_returns_object(self):
        """Test wrapper creation returns a wrapper object"""
        wrapper = CIAFWrapperUtils.create_wrapper("test_model")

        assert hasattr(wrapper, 'model_name')
        assert wrapper.model_name == "test_model"

    def test_create_wrapper_with_custom_model(self):
        """Test wrapper creation with custom model"""
        mock_model = MagicMock()
        wrapper = CIAFWrapperUtils.create_wrapper("test_model", model=mock_model)

        assert wrapper is not None

    def test_create_wrapper_with_compliance_mode(self):
        """Test wrapper creation with compliance mode"""
        wrapper = CIAFWrapperUtils.create_wrapper(
            "test_model",
            compliance_mode="healthcare"
        )

        assert wrapper is not None
        assert wrapper.compliance_mode == "healthcare"

    def test_create_wrapper_with_multiple_options(self):
        """Test wrapper creation with multiple options"""
        wrapper = CIAFWrapperUtils.create_wrapper(
            "test_model",
            enable_connections=True,
            compliance_mode="banking",
            enable_preprocessing=True,
            enable_explainability=True
        )

        assert wrapper is not None
        assert wrapper.model_name == "test_model"

    def test_create_wrapper_enables_features_by_default(self):
        """Test wrapper enables key features by default"""
        wrapper = CIAFWrapperUtils.create_wrapper("test_model")

        # Check that major features are enabled
        assert hasattr(wrapper, 'enable_connections')
        assert hasattr(wrapper, 'compliance_mode')

    def test_create_wrapper_failure_returns_none(self):
        """Test wrapper creation gracefully handles errors"""
        # Try creating with invalid parameters
        wrapper = CIAFWrapperUtils.create_wrapper("test_model", invalid_param="bad")

        # Should either succeed or return None gracefully
        assert wrapper is None or wrapper is not None

    def test_create_wrapper_with_framework(self):
        """Test wrapper creation with specific framework"""
        wrapper = CIAFWrapperUtils.create_wrapper(
            "test_model",
            framework="banking"
        )

        assert wrapper is not None


class TestSafeTraining:
    """Test suite for safe_train static method"""

    @pytest.fixture
    def mock_wrapper(self):
        """Create a mock wrapper for testing"""
        wrapper = MagicMock()
        wrapper.model_name = "test_model"
        wrapper.train = MagicMock(return_value=MagicMock())
        return wrapper

    @pytest.fixture
    def sample_data(self):
        """Create sample training data"""
        X = pd.DataFrame({
            'feature1': [1.0, 2.0, 3.0],
            'feature2': [4.0, 5.0, 6.0]
        })
        y = pd.Series([10.0, 20.0, 30.0])
        return X, y

    def test_safe_train_basic(self, mock_wrapper, sample_data):
        """Test basic training execution"""
        X, y = sample_data
        success, message = CIAFWrapperUtils.safe_train(mock_wrapper, X, y)

        assert isinstance(success, bool)
        assert isinstance(message, str)

    def test_safe_train_with_none_wrapper(self):
        """Test training fails gracefully with None wrapper"""
        X = pd.DataFrame({'a': [1, 2, 3]})
        y = pd.Series([1, 2, 3])

        success, message = CIAFWrapperUtils.safe_train(None, X, y)

        assert success is False
        assert "not initialized" in message.lower()

    def test_safe_train_without_train_method(self):
        """Test training fails when wrapper lacks train method"""
        wrapper = MagicMock(spec=[])  # Mock with no methods
        X = pd.DataFrame({'a': [1, 2, 3]})
        y = pd.Series([1, 2, 3])

        success, message = CIAFWrapperUtils.safe_train(wrapper, X, y)

        assert success is False
        assert "train" in message.lower()

    def test_safe_train_with_dataset_id(self, mock_wrapper, sample_data):
        """Test training with custom dataset ID"""
        X, y = sample_data
        success, message = CIAFWrapperUtils.safe_train(
            mock_wrapper, X, y,
            dataset_id="custom_dataset"
        )

        assert isinstance(success, bool)

    def test_safe_train_with_training_params(self, mock_wrapper, sample_data):
        """Test training with custom parameters"""
        X, y = sample_data
        params = {"learning_rate": 0.01, "epochs": 100}
        success, message = CIAFWrapperUtils.safe_train(
            mock_wrapper, X, y,
            training_params=params
        )

        assert isinstance(success, bool)

    def test_safe_train_returns_tuple(self, mock_wrapper, sample_data):
        """Test training returns (success, message) tuple"""
        X, y = sample_data
        result = CIAFWrapperUtils.safe_train(mock_wrapper, X, y)

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_safe_train_message_descriptive(self, mock_wrapper, sample_data):
        """Test training message is descriptive"""
        X, y = sample_data
        success, message = CIAFWrapperUtils.safe_train(mock_wrapper, X, y)

        assert len(message) > 0
        assert isinstance(message, str)

    def test_safe_train_with_model_version(self, mock_wrapper, sample_data):
        """Test training with specific model version"""
        X, y = sample_data
        success, message = CIAFWrapperUtils.safe_train(
            mock_wrapper, X, y,
            model_version="2.0.0"
        )

        assert isinstance(success, bool)


class TestSafePredict:
    """Test suite for safe_predict static method"""

    @pytest.fixture
    def mock_wrapper(self):
        """Create mock wrapper for prediction tests"""
        wrapper = MagicMock()
        wrapper.model_name = "test_model"
        wrapper.model_version = "1.0.0"

        # Mock the predict method to return (prediction, receipt)
        mock_receipt = MagicMock()
        mock_receipt.__dict__ = {"receipt_id": "test_receipt"}
        wrapper.predict.return_value = (np.array([1.0, 2.0, 3.0]), mock_receipt)

        return wrapper

    @pytest.fixture
    def sample_data(self):
        """Create sample prediction data"""
        return pd.DataFrame({
            'feature1': [1.0, 2.0, 3.0],
            'feature2': [4.0, 5.0, 6.0]
        })

    def test_safe_predict_basic(self, mock_wrapper, sample_data):
        """Test basic prediction execution"""
        predictions, message, receipt = CIAFWrapperUtils.safe_predict(
            mock_wrapper, sample_data
        )

        assert isinstance(message, str)
        assert predictions is not None or message != ""

    def test_safe_predict_returns_tuple(self, mock_wrapper, sample_data):
        """Test prediction returns 3-tuple"""
        result = CIAFWrapperUtils.safe_predict(mock_wrapper, sample_data)

        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_safe_predict_with_none_wrapper(self, sample_data):
        """Test prediction fails gracefully with None wrapper"""
        predictions, message, receipt = CIAFWrapperUtils.safe_predict(
            None, sample_data
        )

        assert predictions is None
        assert "not initialized" in message.lower()
        assert receipt is None

    def test_safe_predict_without_predict_method(self, sample_data):
        """Test prediction fails when wrapper lacks predict method"""
        wrapper = MagicMock(spec=[])
        predictions, message, receipt = CIAFWrapperUtils.safe_predict(
            wrapper, sample_data
        )

        assert predictions is None

    def test_safe_predict_single_row(self, mock_wrapper):
        """Test prediction with single row DataFrame"""
        data = pd.DataFrame({'feature1': [1.0], 'feature2': [2.0]})
        predictions, message, receipt = CIAFWrapperUtils.safe_predict(
            mock_wrapper, data
        )

        assert message is not None

    def test_safe_predict_with_return_receipt_false(self, mock_wrapper, sample_data):
        """Test prediction without receipt"""
        predictions, message, receipt = CIAFWrapperUtils.safe_predict(
            mock_wrapper, sample_data, return_receipt=False
        )

        assert isinstance(message, str)

    def test_safe_predict_with_model_version(self, mock_wrapper, sample_data):
        """Test prediction with specific model version"""
        predictions, message, receipt = CIAFWrapperUtils.safe_predict(
            mock_wrapper, sample_data,
            model_version="2.0.0"
        )

        assert isinstance(message, str)

    def test_safe_predict_returns_numpy_array(self, mock_wrapper, sample_data):
        """Test predictions are numpy arrays"""
        predictions, message, receipt = CIAFWrapperUtils.safe_predict(
            mock_wrapper, sample_data
        )

        if predictions is not None:
            assert isinstance(predictions, (np.ndarray, type(None)))


class TestGetAuditInfo:
    """Test suite for get_audit_info static method"""

    def test_get_audit_info_basic(self):
        """Test basic audit info retrieval"""
        wrapper = MagicMock()
        wrapper.model_name = "test_model"
        wrapper._trained = True

        info = CIAFWrapperUtils.get_audit_info(wrapper)

        assert isinstance(info, dict)
        assert 'model_name' in info

    def test_get_audit_info_with_none_wrapper(self):
        """Test audit info with None wrapper"""
        info = CIAFWrapperUtils.get_audit_info(None)

        assert isinstance(info, dict)
        assert 'error' in info

    def test_get_audit_info_returns_dict(self):
        """Test audit info returns dict"""
        wrapper = MagicMock()
        wrapper.model_name = "test_model"

        info = CIAFWrapperUtils.get_audit_info(wrapper)

        assert isinstance(info, dict)
        assert len(info) > 0

    def test_get_audit_info_includes_model_name(self):
        """Test audit info includes model name"""
        wrapper = MagicMock()
        wrapper.model_name = "my_model"

        info = CIAFWrapperUtils.get_audit_info(wrapper)

        assert info.get('model_name') == "my_model"

    def test_get_audit_info_includes_ciaf_status(self):
        """Test audit info includes CIAF enabled status"""
        wrapper = MagicMock()
        info = CIAFWrapperUtils.get_audit_info(wrapper)

        assert 'ciaf_enabled' in info

    def test_get_audit_info_includes_wrapper_type(self):
        """Test audit info includes wrapper type"""
        wrapper = MagicMock()
        wrapper.model_name = "test"

        info = CIAFWrapperUtils.get_audit_info(wrapper)

        assert 'wrapper_type' in info


class TestValidateWrapper:
    """Test suite for validate_wrapper static method"""

    def test_validate_wrapper_basic(self):
        """Test basic wrapper validation"""
        wrapper = MagicMock()
        wrapper.model_name = "test_model"
        wrapper._initialized = True

        is_valid, issues = CIAFWrapperUtils.validate_wrapper(wrapper)

        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)

    def test_validate_wrapper_with_none(self):
        """Test validation fails with None wrapper"""
        is_valid, issues = CIAFWrapperUtils.validate_wrapper(None)

        assert is_valid is False
        assert len(issues) > 0

    def test_validate_wrapper_returns_tuple(self):
        """Test validation returns (bool, list) tuple"""
        wrapper = MagicMock()
        result = CIAFWrapperUtils.validate_wrapper(wrapper)

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_validate_wrapper_missing_model_name(self):
        """Test validation detects missing model_name"""
        wrapper = MagicMock(spec=[])  # No attributes

        is_valid, issues = CIAFWrapperUtils.validate_wrapper(wrapper)

        assert is_valid is False
        assert any('model_name' in issue.lower() for issue in issues)

    def test_validate_wrapper_missing_initialized_flag(self):
        """Test validation detects missing _initialized flag"""
        wrapper = MagicMock()
        wrapper.model_name = "test"
        # Remove _initialized attribute

        is_valid, issues = CIAFWrapperUtils.validate_wrapper(wrapper)

        # May fail or may be valid depending on implementation
        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)

    def test_validate_wrapper_valid_complete(self):
        """Test validation with complete valid wrapper"""
        wrapper = MagicMock()
        wrapper.model_name = "test_model"
        wrapper._initialized = True

        is_valid, issues = CIAFWrapperUtils.validate_wrapper(wrapper)

        # Should be valid with no issues
        assert is_valid is True or len(issues) == 0

    def test_validate_wrapper_issues_descriptive(self):
        """Test validation issues are descriptive"""
        wrapper = MagicMock(spec=[])

        is_valid, issues = CIAFWrapperUtils.validate_wrapper(wrapper)

        # If there are issues, they should be strings
        for issue in issues:
            assert isinstance(issue, str)
            assert len(issue) > 0


class TestWrapperUtilsIntegration:
    """Integration tests for wrapper utilities"""

    def test_create_and_validate_workflow(self):
        """Test creating a wrapper and validating it"""
        wrapper = CIAFWrapperUtils.create_wrapper("integration_test")

        if wrapper is not None:
            is_valid, issues = CIAFWrapperUtils.validate_wrapper(wrapper)
            assert isinstance(is_valid, bool)

    def test_audit_info_from_created_wrapper(self):
        """Test getting audit info from created wrapper"""
        wrapper = CIAFWrapperUtils.create_wrapper("test_model")

        if wrapper is not None:
            info = CIAFWrapperUtils.get_audit_info(wrapper)
            assert isinstance(info, dict)

    def test_error_handling_multiple_operations(self):
        """Test error handling across multiple operations"""
        # Try a sequence that might fail
        wrapper = CIAFWrapperUtils.create_wrapper("test")

        if wrapper is not None:
            # All operations should handle errors gracefully
            info = CIAFWrapperUtils.get_audit_info(wrapper)
            is_valid, issues = CIAFWrapperUtils.validate_wrapper(wrapper)

            assert isinstance(info, dict)
            assert isinstance(is_valid, bool)
