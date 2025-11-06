"""Fuzzy matching algorithms for dataset comparison"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from fuzzywuzzy import fuzz
import jellyfish
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataMatcher:
    """Performs fuzzy matching between datasets"""

    # Match strategies
    EXACT = "exact"
    FUZZY = "fuzzy"
    TOKEN_SORT = "token_sort"
    TOKEN_SET = "token_set"
    PHONETIC = "phonetic"

    def __init__(self, threshold: float = 80.0):
        """
        Initialize DataMatcher

        Args:
            threshold: Minimum match percentage (0-100) to consider a match
        """
        self.threshold = threshold

    @staticmethod
    def fuzzy_match(source_val: str, target_val: str, strategy: str = FUZZY) -> Tuple[float, str]:
        """
        Calculate fuzzy match percentage between two values

        Args:
            source_val: Value from source dataset
            target_val: Value from target dataset
            strategy: Matching strategy to use

        Returns:
            Tuple of (match_percentage, match_type)
        """
        # Handle null values
        if pd.isna(source_val) or pd.isna(target_val):
            return 0.0, "null_value"

        # Convert to strings
        str_source = str(source_val).strip()
        str_target = str(target_val).strip()

        # Check for exact match first
        if str_source.lower() == str_target.lower():
            return 100.0, DataMatcher.EXACT

        # Apply the requested strategy
        if strategy == DataMatcher.EXACT:
            return 0.0, "no_match"

        elif strategy == DataMatcher.FUZZY:
            score = fuzz.ratio(str_source.lower(), str_target.lower())
            return float(score), DataMatcher.FUZZY

        elif strategy == DataMatcher.TOKEN_SORT:
            score = fuzz.token_sort_ratio(str_source.lower(), str_target.lower())
            return float(score), DataMatcher.TOKEN_SORT

        elif strategy == DataMatcher.TOKEN_SET:
            score = fuzz.token_set_ratio(str_source.lower(), str_target.lower())
            return float(score), DataMatcher.TOKEN_SET

        elif strategy == DataMatcher.PHONETIC:
            # Use metaphone for phonetic matching
            try:
                source_phonetic = jellyfish.metaphone(str_source)
                target_phonetic = jellyfish.metaphone(str_target)

                if source_phonetic == target_phonetic:
                    return 95.0, DataMatcher.PHONETIC
                else:
                    # Fall back to fuzzy matching
                    score = fuzz.ratio(str_source.lower(), str_target.lower())
                    return float(score), DataMatcher.FUZZY
            except Exception:
                # Fall back to fuzzy matching on error
                score = fuzz.ratio(str_source.lower(), str_target.lower())
                return float(score), DataMatcher.FUZZY

        else:
            # Default to fuzzy ratio
            score = fuzz.ratio(str_source.lower(), str_target.lower())
            return float(score), DataMatcher.FUZZY

    def find_best_match(self, source_val: str, target_series: pd.Series,
                       strategy: str = FUZZY) -> Tuple[Optional[int], float, str]:
        """
        Find the best match for a source value in target series

        Args:
            source_val: Value to match
            target_series: Series of potential matches
            strategy: Matching strategy to use

        Returns:
            Tuple of (target_index, match_score, match_type)
        """
        best_idx = None
        best_score = 0.0
        best_type = "no_match"

        for idx, target_val in target_series.items():
            score, match_type = self.fuzzy_match(source_val, target_val, strategy)

            if score > best_score:
                best_score = score
                best_idx = idx
                best_type = match_type

        if best_score >= self.threshold:
            return best_idx, best_score, best_type
        else:
            return None, best_score, "no_match"

    def match_datasets(self, source_df: pd.DataFrame, target_df: pd.DataFrame,
                      column_mapping: Dict[str, str],
                      strategy: str = FUZZY,
                      use_parallel: bool = True) -> pd.DataFrame:
        """
        Match entire datasets based on mapped columns

        Args:
            source_df: Source DataFrame
            target_df: Target DataFrame
            column_mapping: Dictionary mapping source columns to target columns
            strategy: Matching strategy to use
            use_parallel: Whether to use parallel processing

        Returns:
            DataFrame with match results
        """
        logger.info(f"Starting dataset matching with {len(source_df)} source rows and {len(target_df)} target rows")
        logger.info(f"Using strategy: {strategy}, threshold: {self.threshold}")

        results = []

        # Track which target rows have been matched
        matched_target_indices = set()

        if use_parallel and len(source_df) > 100:
            results = self._match_parallel(source_df, target_df, column_mapping, strategy, matched_target_indices)
        else:
            results = self._match_sequential(source_df, target_df, column_mapping, strategy, matched_target_indices)

        # Create results DataFrame
        results_df = pd.DataFrame(results)

        logger.info(f"Matching complete. Found {len(results_df[results_df['match_status'] != 'no_match'])} matches")

        return results_df

    def _match_sequential(self, source_df: pd.DataFrame, target_df: pd.DataFrame,
                         column_mapping: Dict[str, str], strategy: str,
                         matched_target_indices: set) -> List[Dict]:
        """Sequential matching implementation"""
        results = []

        for idx, source_row in source_df.iterrows():
            result = self._match_single_row(idx, source_row, target_df, column_mapping,
                                           strategy, matched_target_indices)
            results.append(result)

        return results

    def _match_parallel(self, source_df: pd.DataFrame, target_df: pd.DataFrame,
                       column_mapping: Dict[str, str], strategy: str,
                       matched_target_indices: set) -> List[Dict]:
        """Parallel matching implementation"""
        results = []
        max_workers = min(4, len(source_df))  # Limit to 4 workers

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._match_single_row, idx, row, target_df,
                              column_mapping, strategy, matched_target_indices): idx
                for idx, row in source_df.iterrows()
            }

            for future in as_completed(futures):
                results.append(future.result())

        # Sort results by source index to maintain order
        results.sort(key=lambda x: x['source_index'])

        return results

    def _match_single_row(self, idx: int, source_row: pd.Series, target_df: pd.DataFrame,
                         column_mapping: Dict[str, str], strategy: str,
                         matched_target_indices: set) -> Dict:
        """Match a single source row against target dataset"""

        # Calculate composite match score across all mapped columns
        best_overall_idx = None
        best_overall_score = 0.0
        best_match_type = "no_match"
        column_scores = {}

        for target_idx, target_row in target_df.iterrows():
            # Skip already matched targets
            if target_idx in matched_target_indices:
                continue

            scores = []
            for source_col, target_col in column_mapping.items():
                score, match_type = self.fuzzy_match(
                    source_row[source_col],
                    target_row[target_col],
                    strategy
                )
                scores.append(score)

            # Calculate average score across all columns
            avg_score = np.mean(scores) if scores else 0.0

            if avg_score > best_overall_score:
                best_overall_score = avg_score
                best_overall_idx = target_idx
                best_match_type = "fuzzy" if avg_score < 100 else "exact"
                column_scores = {
                    source_col: scores[i]
                    for i, source_col in enumerate(column_mapping.keys())
                }

        # Build result record
        result = {
            'source_index': idx,
            'match_percentage': round(best_overall_score, 2),
            'match_status': best_match_type if best_overall_score >= self.threshold else 'no_match',
        }

        # Add source columns
        for source_col in column_mapping.keys():
            result[f'source_{source_col}'] = source_row[source_col]

        # Add target columns if match found
        if best_overall_idx is not None and best_overall_score >= self.threshold:
            result['target_index'] = best_overall_idx
            matched_target_indices.add(best_overall_idx)

            target_row = target_df.iloc[best_overall_idx]
            for source_col, target_col in column_mapping.items():
                result[f'target_{target_col}'] = target_row[target_col]
                result[f'column_score_{source_col}'] = column_scores.get(source_col, 0.0)
        else:
            result['target_index'] = None
            for target_col in column_mapping.values():
                result[f'target_{target_col}'] = None
            for source_col in column_mapping.keys():
                result[f'column_score_{source_col}'] = 0.0

        return result

    @staticmethod
    def get_match_statistics(results_df: pd.DataFrame) -> Dict:
        """
        Calculate statistics from match results

        Args:
            results_df: DataFrame with match results

        Returns:
            Dictionary with match statistics
        """
        total_rows = len(results_df)

        if total_rows == 0:
            return {
                'total_rows': 0,
                'exact_matches': 0,
                'fuzzy_matches': 0,
                'no_matches': 0,
                'match_rate': 0.0,
                'avg_match_score': 0.0
            }

        exact_matches = len(results_df[results_df['match_status'] == 'exact'])
        fuzzy_matches = len(results_df[results_df['match_status'] == 'fuzzy'])
        no_matches = len(results_df[results_df['match_status'] == 'no_match'])

        total_matches = exact_matches + fuzzy_matches
        match_rate = (total_matches / total_rows) * 100

        avg_match_score = results_df['match_percentage'].mean()

        return {
            'total_rows': total_rows,
            'exact_matches': exact_matches,
            'fuzzy_matches': fuzzy_matches,
            'no_matches': no_matches,
            'match_rate': round(match_rate, 2),
            'avg_match_score': round(avg_match_score, 2)
        }
