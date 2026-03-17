"""
Test suite for CIAF Data Utilities
Tests data format conversion, validation, and transformation
"""

import pytest
import pandas as pd
import numpy as np
from typing import List, Dict, Any

from ciaf.utils.data_utils import CIAFDataUtils


class TestCIAFDataUtilsToFormat:
    """Test suite for to_ciaf_format method"""

    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample DataFrame for testing"""
        return pd.DataFrame({
            'feature1': [1.0, 2.0, 3.0],
            'feature2': [4.0, 5.0, 6.0],
            'feature3': [7.0, 8.0, 9.0],
        })

    @pytest.fixture
    def sample_series(self):
        """Create a sample target Series"""
        return pd.Series([10.0, 20.0, 30.0])

    def test_to_ciaf_format_basic(self, sample_dataframe):
        """Test basic conversion to CIAF format"""
        result = CIAFDataUtils.to_ciaf_format(sample_dataframe)

        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(item, dict) for item in result)

    def test_to_ciaf_format_structure(self, sample_dataframe):
        """Test CIAF format has required structure"""
        result = CIAFDataUtils.to_ciaf_format(sample_dataframe)

        for record in result:
            assert 'content' in record
            assert 'metadata' in record
            assert isinstance(record['content'], dict)
            assert isinstance(record['metadata'], dict)

    def test_to_ciaf_format_content_field(self, sample_dataframe):
        """Test content field contains feature data"""
        result = CIAFDataUtils.to_ciaf_format(sample_dataframe)

        first_record = result[0]
        content = first_record['content']

        assert 'feature1' in content
        assert 'feature2' in content
        assert 'feature3' in content
        assert content['feature1'] == 1.0

    def test_to_ciaf_format_metadata_fields(self, sample_dataframe):
        """Test metadata contains required fields"""
        result = CIAFDataUtils.to_ciaf_format(sample_dataframe)

        for i, record in enumerate(result):
            metadata = record['metadata']
            assert 'id' in metadata
            assert 'index' in metadata
            assert 'feature_names' in metadata
            assert metadata['id'] == str(i)
            assert metadata['index'] == i

    def test_to_ciaf_format_with_target_series(self, sample_dataframe, sample_series):
        """Test conversion includes target variable when provided"""
        result = CIAFDataUtils.to_ciaf_format(sample_dataframe, sample_series)

        for i, record in enumerate(result):
            assert 'target' in record['metadata']
            assert record['metadata']['target'] == sample_series.iloc[i]

    def test_to_ciaf_format_without_target_series(self, sample_dataframe):
        """Test conversion without target variable"""
        result = CIAFDataUtils.to_ciaf_format(sample_dataframe)

        for record in result:
            assert 'target' not in record['metadata']

    def test_to_ciaf_format_feature_names(self, sample_dataframe):
        """Test feature names are correctly recorded"""
        result = CIAFDataUtils.to_ciaf_format(sample_dataframe)

        expected_features = list(sample_dataframe.columns)
        assert result[0]['metadata']['feature_names'] == expected_features

    def test_to_ciaf_format_single_row(self):
        """Test conversion with single row DataFrame"""
        df = pd.DataFrame({'a': [1], 'b': [2]})
        result = CIAFDataUtils.to_ciaf_format(df)

        assert len(result) == 1
        assert result[0]['content']['a'] == 1
        assert result[0]['content']['b'] == 2

    def test_to_ciaf_format_large_dataframe(self):
        """Test conversion with large DataFrame"""
        df = pd.DataFrame({f'feature_{i}': range(1000) for i in range(10)})
        result = CIAFDataUtils.to_ciaf_format(df)

        assert len(result) == 1000
        assert result[0]['metadata']['id'] == '0'
        assert result[999]['metadata']['id'] == '999'

    def test_to_ciaf_format_with_strings(self):
        """Test conversion with string features"""
        df = pd.DataFrame({
            'text': ['hello', 'world', 'test'],
            'value': [1, 2, 3]
        })
        result = CIAFDataUtils.to_ciaf_format(df)

        assert result[0]['content']['text'] == 'hello'
        assert result[1]['content']['text'] == 'world'

    def test_to_ciaf_format_with_mixed_types(self):
        """Test conversion with mixed data types"""
        df = pd.DataFrame({
            'int_col': [1, 2, 3],
            'float_col': [1.5, 2.5, 3.5],
            'str_col': ['a', 'b', 'c'],
        })
        result = CIAFDataUtils.to_ciaf_format(df)

        assert result[0]['content']['int_col'] == 1
        assert result[0]['content']['float_col'] == 1.5
        assert result[0]['content']['str_col'] == 'a'


class TestCIAFDataUtilsValidate:
    """Test suite for validate method"""

    @pytest.fixture
    def valid_data(self):
        """Create valid CIAF formatted data"""
        return [
            {
                'content': {'a': 1, 'b': 2},
                'metadata': {'id': '0', 'index': 0}
            },
            {
                'content': {'a': 3, 'b': 4},
                'metadata': {'id': '1', 'index': 1}
            }
        ]

    def test_validate_valid_data(self, valid_data):
        """Test validation passes for valid data"""
        is_valid, errors = CIAFDataUtils.validate(valid_data)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_not_a_list(self):
        """Test validation fails when data is not a list"""
        is_valid, errors = CIAFDataUtils.validate({'not': 'list'})

        assert is_valid is False
        assert len(errors) > 0
        assert any('list' in error.lower() for error in errors)

    def test_validate_empty_list(self):
        """Test validation fails for empty list"""
        is_valid, errors = CIAFDataUtils.validate([])

        assert is_valid is False
        assert len(errors) > 0

    def test_validate_missing_content_field(self):
        """Test validation fails when content is missing"""
        data = [{'metadata': {'id': '0'}}]
        is_valid, errors = CIAFDataUtils.validate(data)

        assert is_valid is False
        assert any('content' in error.lower() for error in errors)

    def test_validate_missing_metadata_field(self):
        """Test validation fails when metadata is missing"""
        data = [{'content': {'a': 1}}]
        is_valid, errors = CIAFDataUtils.validate(data)

        assert is_valid is False
        assert any('metadata' in error.lower() for error in errors)

    def test_validate_metadata_not_dict(self):
        """Test validation fails when metadata is not a dict"""
        data = [
            {
                'content': {'a': 1},
                'metadata': 'not_a_dict'
            }
        ]
        is_valid, errors = CIAFDataUtils.validate(data)

        assert is_valid is False

    def test_validate_missing_id_in_metadata(self):
        """Test validation fails when metadata missing id"""
        data = [
            {
                'content': {'a': 1},
                'metadata': {'index': 0}
            }
        ]
        is_valid, errors = CIAFDataUtils.validate(data)

        assert is_valid is False
        assert any('id' in error.lower() for error in errors)

    def test_validate_record_not_dict(self):
        """Test validation fails when record is not a dict"""
        data = ['not_a_dict']
        is_valid, errors = CIAFDataUtils.validate(data)

        assert is_valid is False

    def test_validate_multiple_errors(self):
        """Test validation collects multiple errors"""
        data = [
            {'metadata': {'id': '0'}},  # Missing content
            {'content': {'a': 1}},       # Missing metadata
        ]
        is_valid, errors = CIAFDataUtils.validate(data)

        assert is_valid is False
        assert len(errors) >= 2


class TestCIAFDataUtilsFromFormat:
    """Test suite for from_ciaf_format method"""

    @pytest.fixture
    def ciaf_data(self):
        """Create CIAF formatted data"""
        return [
            {
                'content': {'a': 1.0, 'b': 2.0},
                'metadata': {'id': '0', 'target': 10.0}
            },
            {
                'content': {'a': 3.0, 'b': 4.0},
                'metadata': {'id': '1', 'target': 20.0}
            }
        ]

    def test_from_ciaf_format_basic(self, ciaf_data):
        """Test basic conversion from CIAF format"""
        X, y = CIAFDataUtils.from_ciaf_format(ciaf_data)

        assert isinstance(X, pd.DataFrame)
        assert isinstance(y, (pd.Series, type(None)))

    def test_from_ciaf_format_dataframe_shape(self, ciaf_data):
        """Test DataFrame has correct shape"""
        X, y = CIAFDataUtils.from_ciaf_format(ciaf_data)

        assert X.shape[0] == 2
        assert X.shape[1] == 2  # 'a' and 'b'

    def test_from_ciaf_format_dataframe_values(self, ciaf_data):
        """Test DataFrame contains correct values"""
        X, y = CIAFDataUtils.from_ciaf_format(ciaf_data)

        assert X.iloc[0, 0] == 1.0  # First row, first column
        assert X.iloc[1, 1] == 4.0  # Second row, second column

    def test_from_ciaf_format_target_series(self, ciaf_data):
        """Test target Series is extracted correctly"""
        X, y = CIAFDataUtils.from_ciaf_format(ciaf_data)

        assert y is not None
        assert isinstance(y, pd.Series)
        assert len(y) == 2
        assert y.iloc[0] == 10.0
        assert y.iloc[1] == 20.0

    def test_from_ciaf_format_without_targets(self):
        """Test conversion when no targets are provided"""
        data = [
            {
                'content': {'a': 1.0},
                'metadata': {'id': '0'}
            }
        ]
        X, y = CIAFDataUtils.from_ciaf_format(data)

        assert y is None

    def test_from_ciaf_format_empty_data(self):
        """Test conversion with empty data"""
        X, y = CIAFDataUtils.from_ciaf_format([])

        assert X.shape[0] == 0
        assert y is None

    def test_from_ciaf_format_roundtrip(self):
        """Test roundtrip conversion preserves data"""
        original_df = pd.DataFrame({
            'a': [1.0, 2.0, 3.0],
            'b': [4.0, 5.0, 6.0]
        })
        original_series = pd.Series([10.0, 20.0, 30.0])

        ciaf_data = CIAFDataUtils.to_ciaf_format(original_df, original_series)
        recovered_df, recovered_series = CIAFDataUtils.from_ciaf_format(ciaf_data)

        pd.testing.assert_frame_equal(original_df, recovered_df)
        pd.testing.assert_series_equal(original_series, recovered_series)


class TestCIAFDataUtilsGetSchema:
    """Test suite for get_schema method"""

    def test_get_schema_basic(self):
        """Test basic schema generation"""
        data = [
            {
                'content': {'a': 1, 'b': 2.0},
                'metadata': {'id': '0'}
            }
        ]
        schema = CIAFDataUtils.get_schema(data)

        assert isinstance(schema, dict)
        assert len(schema) > 0

    def test_get_schema_empty_data(self):
        """Test schema with empty data"""
        schema = CIAFDataUtils.get_schema([])

        assert schema == {}

    def test_get_schema_types(self):
        """Test schema correctly identifies types"""
        data = [
            {
                'content': {'int_field': 1, 'float_field': 2.0},
                'metadata': {'id': '0', 'target': 5.0}
            }
        ]
        schema = CIAFDataUtils.get_schema(data)

        assert 'target' in schema
        assert schema['target'] == 'float'

    def test_get_schema_with_string_features(self):
        """Test schema with string features"""
        data = [
            {
                'content': {'text': 'hello'},
                'metadata': {'id': '0'}
            }
        ]
        schema = CIAFDataUtils.get_schema(data)

        assert 'feature_text' in schema
        assert schema['feature_text'] == 'str'

    def test_get_schema_multiple_types(self):
        """Test schema with various data types"""
        data = [
            {
                'content': {
                    'int_val': 42,
                    'float_val': 3.14,
                    'str_val': 'test',
                    'bool_val': True
                },
                'metadata': {'id': '0'}
            }
        ]
        schema = CIAFDataUtils.get_schema(data)

        assert 'feature_int_val' in schema
        assert 'feature_float_val' in schema
        assert 'feature_str_val' in schema
        assert 'feature_bool_val' in schema
