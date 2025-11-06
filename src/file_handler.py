"""File handling operations for CSV and Excel files"""

import pandas as pd
import io
from typing import Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileHandler:
    """Handles file loading and validation for CSV and Excel files"""

    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB in bytes
    SUPPORTED_EXTENSIONS = ['.csv', '.xlsx', '.xls']

    @staticmethod
    def validate_file(file) -> Tuple[bool, str]:
        """
        Validate uploaded file

        Args:
            file: Uploaded file object from Streamlit

        Returns:
            Tuple of (is_valid, error_message)
        """
        if file is None:
            return False, "No file provided"

        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        if file_size > FileHandler.MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            return False, f"File size ({size_mb:.2f}MB) exceeds maximum allowed size (100MB)"

        if file_size == 0:
            return False, "File is empty"

        # Check file extension
        file_name = file.name.lower()
        if not any(file_name.endswith(ext) for ext in FileHandler.SUPPORTED_EXTENSIONS):
            return False, f"Unsupported file format. Supported formats: {', '.join(FileHandler.SUPPORTED_EXTENSIONS)}"

        return True, ""

    @staticmethod
    def load_dataset(file, encoding: str = 'utf-8') -> Tuple[Optional[pd.DataFrame], str]:
        """
        Load dataset from CSV or Excel file

        Args:
            file: Uploaded file object
            encoding: Character encoding for CSV files (default: utf-8)

        Returns:
            Tuple of (DataFrame, error_message). DataFrame is None if loading fails.
        """
        # Validate file first
        is_valid, error_msg = FileHandler.validate_file(file)
        if not is_valid:
            return None, error_msg

        file_name = file.name.lower()

        try:
            if file_name.endswith('.csv'):
                # Try loading CSV with specified encoding
                try:
                    df = pd.read_csv(file, encoding=encoding)
                except UnicodeDecodeError:
                    # Try alternative encodings
                    logger.info(f"Failed to load with {encoding}, trying latin-1")
                    file.seek(0)
                    try:
                        df = pd.read_csv(file, encoding='latin-1')
                    except Exception:
                        file.seek(0)
                        df = pd.read_csv(file, encoding='iso-8859-1')

            elif file_name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file, engine='openpyxl' if file_name.endswith('.xlsx') else None)
            else:
                return None, f"Unsupported file format: {file_name}"

            # Validate loaded data
            if df.empty:
                return None, "File contains no data"

            if df.shape[1] == 0:
                return None, "File contains no columns"

            logger.info(f"Successfully loaded file: {file.name} with shape {df.shape}")
            return df, ""

        except Exception as e:
            logger.error(f"Error loading file {file.name}: {str(e)}")
            return None, f"Error loading file: {str(e)}"

    @staticmethod
    def get_file_info(df: pd.DataFrame) -> dict:
        """
        Get summary information about a DataFrame

        Args:
            df: Input DataFrame

        Returns:
            Dictionary with file information
        """
        return {
            'rows': df.shape[0],
            'columns': df.shape[1],
            'column_names': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum() / (1024 * 1024)  # MB
        }
