"""Tests for the file_handler module"""

import pytest
import pandas as pd
import io
from src.file_handler import FileHandler


class TestFileValidation:
    """Test file validation functionality"""

    def test_validate_none_file(self):
        """Test validation with None file"""
        is_valid, error = FileHandler.validate_file(None)
        assert not is_valid
        assert "No file provided" in error

    def test_validate_empty_file(self):
        """Test validation with empty file"""
        # Create a mock empty file
        mock_file = io.BytesIO(b"")
        mock_file.name = "test.csv"
        mock_file.seek = lambda x, y=0: None
        mock_file.tell = lambda: 0

        is_valid, error = FileHandler.validate_file(mock_file)
        assert not is_valid
        assert "empty" in error.lower()

    def test_validate_unsupported_format(self):
        """Test validation with unsupported file format"""
        mock_file = io.BytesIO(b"some data")
        mock_file.name = "test.txt"
        mock_file.seek = lambda x, y=0: None
        mock_file.tell = lambda: 100

        is_valid, error = FileHandler.validate_file(mock_file)
        assert not is_valid
        assert "Unsupported file format" in error


class TestFileLoading:
    """Test file loading functionality"""

    @pytest.fixture
    def sample_csv_file(self):
        """Create a sample CSV file"""
        csv_data = """name,age,city
John Doe,30,New York
Jane Smith,25,Los Angeles
Bob Johnson,35,Chicago"""

        file = io.BytesIO(csv_data.encode('utf-8'))
        file.name = "test.csv"
        return file

    @pytest.fixture
    def sample_excel_file(self):
        """Create a sample Excel file"""
        df = pd.DataFrame({
            'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'age': [30, 25, 35],
            'city': ['New York', 'Los Angeles', 'Chicago']
        })

        file = io.BytesIO()
        df.to_excel(file, index=False)
        file.seek(0)
        file.name = "test.xlsx"
        return file

    def test_load_csv_file(self, sample_csv_file):
        """Test loading a CSV file"""
        df, error = FileHandler.load_dataset(sample_csv_file)

        assert error == ""
        assert df is not None
        assert len(df) == 3
        assert list(df.columns) == ['name', 'age', 'city']

    def test_load_excel_file(self, sample_excel_file):
        """Test loading an Excel file"""
        df, error = FileHandler.load_dataset(sample_excel_file)

        assert error == ""
        assert df is not None
        assert len(df) == 3
        assert 'name' in df.columns


class TestFileInfo:
    """Test file information extraction"""

    def test_get_file_info(self):
        """Test getting information about a DataFrame"""
        df = pd.DataFrame({
            'col1': [1, 2, 3, None, 5],
            'col2': ['a', 'b', 'c', 'd', 'e']
        })

        info = FileHandler.get_file_info(df)

        assert info['rows'] == 5
        assert info['columns'] == 2
        assert info['column_names'] == ['col1', 'col2']
        assert 'dtypes' in info
        assert 'missing_values' in info
        assert info['missing_values']['col1'] == 1
        assert info['missing_values']['col2'] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
