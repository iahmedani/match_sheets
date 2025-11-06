"""Tests for the matcher module"""

import pytest
import pandas as pd
from src.matcher import DataMatcher


class TestFuzzyMatch:
    """Test the fuzzy matching functionality"""

    def test_exact_match(self):
        """Test exact string matching"""
        score, match_type = DataMatcher.fuzzy_match("John Smith", "John Smith")
        assert score == 100.0
        assert match_type == DataMatcher.EXACT

    def test_case_insensitive(self):
        """Test case insensitive matching"""
        score, match_type = DataMatcher.fuzzy_match("JOHN SMITH", "john smith")
        assert score == 100.0
        assert match_type == DataMatcher.EXACT

    def test_fuzzy_match_high_similarity(self):
        """Test fuzzy matching with high similarity"""
        score, match_type = DataMatcher.fuzzy_match("John Smith", "Jon Smith")
        assert score >= 90.0
        assert match_type == DataMatcher.FUZZY

    def test_fuzzy_match_low_similarity(self):
        """Test fuzzy matching with low similarity"""
        score, match_type = DataMatcher.fuzzy_match("John Smith", "Jane Doe")
        assert score < 50.0

    def test_null_values(self):
        """Test handling of null values"""
        score, match_type = DataMatcher.fuzzy_match(None, "John Smith")
        assert score == 0.0
        assert match_type == "null_value"

    def test_token_sort_strategy(self):
        """Test token sort matching strategy"""
        score, match_type = DataMatcher.fuzzy_match(
            "John Smith",
            "Smith John",
            strategy=DataMatcher.TOKEN_SORT
        )
        assert score >= 95.0  # Should be very high for reordered words


class TestDataMatcher:
    """Test the DataMatcher class"""

    @pytest.fixture
    def sample_data(self):
        """Create sample dataframes for testing"""
        source_df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['John Smith', 'Jane Doe', 'Bob Johnson'],
            'email': ['john@email.com', 'jane@email.com', 'bob@email.com']
        })

        target_df = pd.DataFrame({
            'customer_id': [101, 102, 103],
            'full_name': ['Smith John', 'Jane M. Doe', 'Robert Johnson'],
            'email_address': ['john@email.com', 'jane@email.com', 'bob@email.com']
        })

        return source_df, target_df

    def test_matcher_initialization(self):
        """Test DataMatcher initialization"""
        matcher = DataMatcher(threshold=75.0)
        assert matcher.threshold == 75.0

    def test_find_best_match(self, sample_data):
        """Test finding the best match for a value"""
        source_df, target_df = sample_data
        matcher = DataMatcher(threshold=80.0)

        best_idx, score, match_type = matcher.find_best_match(
            "John Smith",
            target_df['full_name']
        )

        assert best_idx is not None
        assert score >= 80.0

    def test_match_datasets(self, sample_data):
        """Test matching entire datasets"""
        source_df, target_df = sample_data
        matcher = DataMatcher(threshold=70.0)

        column_mapping = {
            'name': 'full_name'
        }

        results = matcher.match_datasets(
            source_df,
            target_df,
            column_mapping,
            use_parallel=False
        )

        assert len(results) == len(source_df)
        assert 'match_percentage' in results.columns
        assert 'match_status' in results.columns

    def test_match_statistics(self, sample_data):
        """Test match statistics calculation"""
        source_df, target_df = sample_data
        matcher = DataMatcher(threshold=70.0)

        column_mapping = {'name': 'full_name'}

        results = matcher.match_datasets(
            source_df,
            target_df,
            column_mapping,
            use_parallel=False
        )

        stats = DataMatcher.get_match_statistics(results)

        assert 'total_rows' in stats
        assert 'exact_matches' in stats
        assert 'fuzzy_matches' in stats
        assert 'no_matches' in stats
        assert 'match_rate' in stats
        assert stats['total_rows'] == len(source_df)


class TestMatchStrategies:
    """Test different matching strategies"""

    def test_phonetic_matching(self):
        """Test phonetic matching for similar-sounding names"""
        score1, _ = DataMatcher.fuzzy_match(
            "Smith",
            "Smyth",
            strategy=DataMatcher.PHONETIC
        )
        assert score1 >= 80.0  # Should match phonetically

    def test_token_set_strategy(self):
        """Test token set matching"""
        score, _ = DataMatcher.fuzzy_match(
            "The Big Company Inc",
            "Big Company",
            strategy=DataMatcher.TOKEN_SET
        )
        assert score >= 70.0  # Should handle extra words


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
