"""Column mapping logic for dataset comparison"""

import pandas as pd
from typing import Dict, List, Tuple
from fuzzywuzzy import fuzz
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ColumnMapper:
    """Handles column mapping between source and target datasets"""

    @staticmethod
    def suggest_mappings(source_columns: List[str], target_columns: List[str],
                        threshold: int = 70) -> Dict[str, str]:
        """
        Suggest column mappings based on name similarity

        Args:
            source_columns: List of column names from source dataset
            target_columns: List of column names from target dataset
            threshold: Minimum similarity score (0-100) for auto-mapping

        Returns:
            Dictionary mapping source columns to target columns
        """
        suggestions = {}

        for source_col in source_columns:
            best_match = None
            best_score = 0

            for target_col in target_columns:
                # Calculate similarity using multiple methods
                ratio_score = fuzz.ratio(source_col.lower(), target_col.lower())
                partial_score = fuzz.partial_ratio(source_col.lower(), target_col.lower())
                token_score = fuzz.token_sort_ratio(source_col.lower(), target_col.lower())

                # Use the maximum score
                score = max(ratio_score, partial_score, token_score)

                if score > best_score:
                    best_score = score
                    best_match = target_col

            if best_score >= threshold:
                suggestions[source_col] = best_match
                logger.info(f"Suggested mapping: '{source_col}' -> '{best_match}' (score: {best_score})")

        return suggestions

    @staticmethod
    def validate_mapping(mapping: Dict[str, str], source_df: pd.DataFrame,
                        target_df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate that mapped columns exist in both datasets

        Args:
            mapping: Dictionary of source to target column mappings
            source_df: Source DataFrame
            target_df: Target DataFrame

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        for source_col, target_col in mapping.items():
            if source_col not in source_df.columns:
                errors.append(f"Source column '{source_col}' not found in source dataset")

            if target_col not in target_df.columns:
                errors.append(f"Target column '{target_col}' not found in target dataset")

        is_valid = len(errors) == 0
        return is_valid, errors

    @staticmethod
    def get_column_info(df: pd.DataFrame, column: str) -> Dict:
        """
        Get detailed information about a column

        Args:
            df: DataFrame
            column: Column name

        Returns:
            Dictionary with column information
        """
        if column not in df.columns:
            return {}

        col_data = df[column]

        return {
            'name': column,
            'dtype': str(col_data.dtype),
            'non_null_count': col_data.count(),
            'null_count': col_data.isnull().sum(),
            'unique_count': col_data.nunique(),
            'sample_values': col_data.dropna().head(5).tolist()
        }
