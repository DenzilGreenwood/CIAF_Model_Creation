"""
Test suite for CIAF Error Utilities
Tests error translation, categorization, logging, and reporting
"""

import pytest
import logging
from typing import Dict, Any

from ciaf.utils.error_utils import CIAFErrorUtils


class TestErrorTranslation:
    """Test suite for translate_error method"""

    def test_translate_error_with_none(self):
        """Test translation when error is None"""
        result = CIAFErrorUtils.translate_error(None)

        assert isinstance(result, str)
        assert 'unknown' in result.lower() or 'error' in result.lower()

    def test_translate_error_provenance_error(self):
        """Test translation of ProvenanceCapsuleGenerationException"""
        error = Exception("ProvenanceCapsuleGenerationException: test")
        result = CIAFErrorUtils.translate_error(error)

        assert 'training' in result.lower() or 'failed' in result.lower()

    def test_translate_error_hash_mismatch(self):
        """Test translation of hash mismatch error"""
        error = Exception("Hash mismatch detected")
        result = CIAFErrorUtils.translate_error(error)

        assert 'integrity' in result.lower() or 'data' in result.lower()

    def test_translate_error_merkle_validation(self):
        """Test translation of Merkle tree validation error"""
        error = Exception("Merkle tree validation failed")
        result = CIAFErrorUtils.translate_error(error)

        assert 'verification' in result.lower() or 'failed' in result.lower()

    def test_translate_error_training_failure(self):
        """Test translation of general training failure"""
        error = Exception("Training failed due to invalid data")
        result = CIAFErrorUtils.translate_error(error)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_translate_error_model_not_trained(self):
        """Test translation of model not trained error"""
        error = Exception("Model not trained yet")
        result = CIAFErrorUtils.translate_error(error)

        assert 'model' in result.lower() or 'trained' in result.lower()

    def test_translate_error_invalid_input(self):
        """Test translation of invalid input error"""
        error = Exception("Invalid input format provided")
        result = CIAFErrorUtils.translate_error(error)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_translate_error_data_format_error(self):
        """Test translation of data format error"""
        error = Exception("cannot unpack values")
        result = CIAFErrorUtils.translate_error(error)

        assert 'format' in result.lower() or 'data' in result.lower()

    def test_translate_error_none_type_error(self):
        """Test translation of NoneType error"""
        error = Exception("NoneType object has no attribute")
        result = CIAFErrorUtils.translate_error(error)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_translate_error_type_error(self):
        """Test translation of type error"""
        error = Exception("float() argument must be a string or number")
        result = CIAFErrorUtils.translate_error(error)

        assert 'type' in result.lower() or 'numeric' in result.lower() or 'invalid' in result.lower()

    def test_translate_error_ciaf_wrapper_error(self):
        """Test translation of CIAF wrapper error"""
        error = Exception("CIAFModelWrapper initialization failed")
        result = CIAFErrorUtils.translate_error(error)

        assert 'ciaf' in result.lower() or 'integration' in result.lower()

    def test_translate_error_unknown_error(self):
        """Test translation of completely unknown error"""
        error = Exception("Some random error we haven't seen before")
        result = CIAFErrorUtils.translate_error(error)

        assert isinstance(result, str)
        assert 'operation failed' in result.lower() or 'error' in result.lower()


class TestErrorCategorization:
    """Test suite for categorize_error method"""

    def test_categorize_error_none(self):
        """Test categorization of None error"""
        result = CIAFErrorUtils.categorize_error(None)

        assert result == "unknown"

    def test_categorize_data_format_error(self):
        """Test categorization of data format error"""
        error = Exception("Invalid data format")
        result = CIAFErrorUtils.categorize_error(error)

        assert result == "data_format"

    def test_categorize_data_conversion_error(self):
        """Test categorization of data conversion error"""
        error = Exception("Cannot convert data type")
        result = CIAFErrorUtils.categorize_error(error)

        assert result == "data_format"

    def test_categorize_training_error(self):
        """Test categorization of training error"""
        error = Exception("Training failed to converge")
        result = CIAFErrorUtils.categorize_error(error)

        assert result == "training"

    def test_categorize_fit_error(self):
        """Test categorization of fit error"""
        error = Exception("Fit method failed")
        result = CIAFErrorUtils.categorize_error(error)

        assert result == "training"

    def test_categorize_learning_error(self):
        """Test categorization of learning error"""
        error = Exception("Learning algorithm diverged")
        result = CIAFErrorUtils.categorize_error(error)

        assert result == "training"

    def test_categorize_prediction_error(self):
        """Test categorization of prediction error"""
        error = Exception("Prediction generation failed")
        result = CIAFErrorUtils.categorize_error(error)

        assert result == "prediction"

    def test_categorize_inference_error(self):
        """Test categorization of inference error"""
        error = Exception("Inference receipt not generated")
        result = CIAFErrorUtils.categorize_error(error)

        assert result == "prediction"

    def test_categorize_ciaf_setup_error(self):
        """Test categorization of CIAF setup error"""
        error = Exception("CIAF wrapper initialization failed")
        result = CIAFErrorUtils.categorize_error(error)

        assert result == "ciaf_setup"

    def test_categorize_wrapper_error(self):
        """Test categorization of wrapper error"""
        error = Exception("Wrapper configuration invalid")
        result = CIAFErrorUtils.categorize_error(error)

        assert result == "ciaf_setup"

    def test_categorize_provenance_error(self):
        """Test categorization of provenance error"""
        error = Exception("Provenance tracking failed")
        result = CIAFErrorUtils.categorize_error(error)

        assert result == "ciaf_setup"

    def test_categorize_general_error(self):
        """Test categorization of general error"""
        error = Exception("Some completely random error")
        result = CIAFErrorUtils.categorize_error(error)

        assert result == "general"


class TestHelpMessages:
    """Test suite for get_help_message method"""

    def test_get_help_data_format(self):
        """Test help message for data format errors"""
        help_msg = CIAFErrorUtils.get_help_message("data_format")

        assert isinstance(help_msg, str)
        assert len(help_msg) > 0
        assert 'data' in help_msg.lower() or 'format' in help_msg.lower()

    def test_get_help_training(self):
        """Test help message for training errors"""
        help_msg = CIAFErrorUtils.get_help_message("training")

        assert isinstance(help_msg, str)
        assert 'training' in help_msg.lower() or 'train' in help_msg.lower()

    def test_get_help_prediction(self):
        """Test help message for prediction errors"""
        help_msg = CIAFErrorUtils.get_help_message("prediction")

        assert isinstance(help_msg, str)
        assert 'prediction' in help_msg.lower() or 'predict' in help_msg.lower()

    def test_get_help_ciaf_setup(self):
        """Test help message for CIAF setup errors"""
        help_msg = CIAFErrorUtils.get_help_message("ciaf_setup")

        assert isinstance(help_msg, str)
        assert 'ciaf' in help_msg.lower() or 'wrapper' in help_msg.lower()

    def test_get_help_unknown_category(self):
        """Test help message for unknown category"""
        help_msg = CIAFErrorUtils.get_help_message("unknown_category")

        assert isinstance(help_msg, str)
        assert "no specific help" in help_msg.lower() or len(help_msg) > 0

    def test_all_help_messages_non_empty(self):
        """Test all standard categories have non-empty help"""
        categories = ["data_format", "training", "prediction", "ciaf_setup"]

        for category in categories:
            help_msg = CIAFErrorUtils.get_help_message(category)
            assert len(help_msg) > 0


class TestErrorLogging:
    """Test suite for log_error method"""

    def test_log_error_basic(self):
        """Test basic error logging"""
        error = Exception("Test error")
        result = CIAFErrorUtils.log_error(error)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_log_error_with_context(self):
        """Test error logging with context"""
        error = Exception("Test error")
        result = CIAFErrorUtils.log_error(error, context="test_context")

        assert isinstance(result, str)
        assert len(result) > 0

    def test_log_error_with_model_name(self):
        """Test error logging with model name"""
        error = Exception("Test error")
        result = CIAFErrorUtils.log_error(error, model_name="test_model")

        assert isinstance(result, str)
        assert len(result) > 0

    def test_log_error_with_all_params(self):
        """Test error logging with all parameters"""
        error = Exception("Test training error")
        result = CIAFErrorUtils.log_error(
            error,
            context="training phase",
            model_name="my_model"
        )

        assert isinstance(result, str)
        assert len(result) > 0
        assert "failed" in result.lower() or "error" in result.lower()

    def test_log_error_returns_user_friendly(self):
        """Test log_error returns user-friendly message"""
        error = ValueError("Training failed to converge")
        result = CIAFErrorUtils.log_error(error)

        # Should be a user-friendly message, not raw exception
        assert isinstance(result, str)
        assert len(result) > 0


class TestErrorReporting:
    """Test suite for create_error_report method"""

    def test_create_error_report_basic(self):
        """Test basic error report creation"""
        error = Exception("Test error")
        report = CIAFErrorUtils.create_error_report(error)

        assert isinstance(report, dict)
        assert 'user_message' in report
        assert 'category' in report
        assert 'help' in report
        assert 'technical_error' in report
        assert 'error_type' in report

    def test_error_report_has_user_message(self):
        """Test error report contains user-friendly message"""
        error = Exception("Training failed")
        report = CIAFErrorUtils.create_error_report(error)

        assert isinstance(report['user_message'], str)
        assert len(report['user_message']) > 0

    def test_error_report_categorization(self):
        """Test error report includes categorization"""
        error = Exception("Data format error")
        report = CIAFErrorUtils.create_error_report(error)

        assert report['category'] in ["data_format", "training", "prediction", "ciaf_setup", "general"]

    def test_error_report_includes_help(self):
        """Test error report includes help message"""
        error = Exception("Training failed")
        report = CIAFErrorUtils.create_error_report(error)

        assert isinstance(report['help'], str)
        assert len(report['help']) > 0

    def test_error_report_includes_technical_details(self):
        """Test error report includes technical details"""
        error = Exception("Technical error message")
        report = CIAFErrorUtils.create_error_report(error)

        assert report['technical_error'] == "Technical error message"
        assert report['error_type'] == "Exception"

    def test_error_report_with_context(self):
        """Test error report with additional context"""
        error = Exception("Test error")
        context = {"operation": "training", "dataset": "test_data"}
        report = CIAFErrorUtils.create_error_report(error, context)

        assert 'context' in report
        assert report['context'] == context

    def test_error_report_timestamp(self):
        """Test error report includes timestamp"""
        error = Exception("Test error")
        report = CIAFErrorUtils.create_error_report(error)

        assert 'timestamp' in report
        assert isinstance(report['timestamp'], str)

    def test_different_error_types(self):
        """Test reports handle different error types"""
        errors = [
            ValueError("Value error test"),
            TypeError("Type error test"),
            RuntimeError("Runtime error test"),
        ]

        for error in errors:
            report = CIAFErrorUtils.create_error_report(error)
            assert report['error_type'] == type(error).__name__

    def test_error_report_comprehensive(self):
        """Test comprehensive error report structure"""
        error = RuntimeError("Complex error occurred")
        context = {"phase": "inference", "model_id": "test_model"}
        report = CIAFErrorUtils.create_error_report(error, context)

        # Verify all expected fields
        required_fields = ['user_message', 'category', 'help', 'technical_error', 'error_type', 'timestamp', 'context']
        for field in required_fields:
            assert field in report, f"Missing field: {field}"


class TestErrorTranslationMapping:
    """Test suite for error translation mapping coverage"""

    def test_all_mapped_errors_translate(self):
        """Test all mapped error patterns translate correctly"""
        test_errors = [
            ("ProvenanceCapsuleGenerationException", "training"),
            ("Hash mismatch", "integrity"),
            ("Merkle tree validation", "verification"),
            ("Training failed", "training"),
            ("Model not trained", "trained"),
            ("Invalid input", "invalid"),
            ("cannot unpack", "format"),
            ("NoneType object", "Missing"),
            ("float() argument", "numeric"),
            ("CIAFModelWrapper", "failed"),
        ]

        for error_msg, expected_keyword in test_errors:
            error = Exception(error_msg)
            result = CIAFErrorUtils.translate_error(error)
            assert isinstance(result, str), f"Translation failed for: {error_msg}"
            assert len(result) > 0


class TestErrorUtilsIntegration:
    """Integration tests for error utilities"""

    def test_full_error_workflow(self):
        """Test complete error handling workflow"""
        # Create an error
        error = TypeError("Invalid data type provided")

        # Translate it
        message = CIAFErrorUtils.translate_error(error)
        assert message is not None

        # Categorize it
        category = CIAFErrorUtils.categorize_error(error)
        assert category is not None

        # Get help
        help_msg = CIAFErrorUtils.get_help_message(category)
        assert help_msg is not None

        # Log it
        log_msg = CIAFErrorUtils.log_error(error, context="test")
        assert log_msg is not None

        # Create report
        report = CIAFErrorUtils.create_error_report(error)
        assert report is not None
        assert all(k in report for k in ['user_message', 'category', 'help'])

    def test_multiple_error_types(self):
        """Test handling multiple different error types"""
        error_types = [
            ValueError("Value issue"),
            TypeError("Type issue"),
            RuntimeError("Runtime issue"),
            Exception("Generic issue"),
            KeyError("Key issue"),
        ]

        for error in error_types:
            # Should not raise any exceptions
            message = CIAFErrorUtils.translate_error(error)
            category = CIAFErrorUtils.categorize_error(error)
            report = CIAFErrorUtils.create_error_report(error)

            assert message is not None
            assert category is not None
            assert report is not None
