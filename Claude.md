# Dataset Comparison Tool - Claude Code Instructions

## Project Context
You are helping to build a Python-based dataset comparison tool that uses fuzzy matching algorithms to find similarities between two datasets. The tool should have a modern web UI using Streamlit and export results to Excel.

## Core Requirements

### 1. File Handling
- Accept CSV and XLSX files as input (source and target datasets)
- Handle various encodings (UTF-8, Latin-1, etc.)
- Validate file formats and provide clear error messages
- Support files up to 100MB

### 2. User Interface (Streamlit)
- Clean, intuitive layout with clear sections
- File uploaders with drag-and-drop support
- Interactive column mapping interface
- Real-time preview of match results
- Progress indicators for long operations
- Export button with download functionality

### 3. Matching Algorithm
- Primary: Fuzzy string matching using fuzzywuzzy library
- Calculate match percentage between records
- Support multiple matching strategies:
  - Exact match
  - Fuzzy match (Levenshtein distance)
  - Token sort ratio (for reordered words)
  - Phonetic matching (for names)
- Allow user-configurable match threshold (default 80%)

### 4. Column Mapping
- Display columns from both datasets side by side
- Allow users to map columns for comparison
- Support one-to-one and many-to-one mappings
- Auto-suggest mappings based on column name similarity

### 5. Excel Export
- Create Excel file with three sheets:
  - `source`: Original source data
  - `target`: Original target data
  - `match_result`: Matching results with:
    - Source ID/key columns
    - Target ID/key columns
    - Match percentage
    - Match status (Exact/Fuzzy/No Match)

## Code Style Guidelines

### Python Best Practices
- Use type hints for all functions
- Follow PEP 8 style guide
- Write docstrings for all classes and functions
- Handle exceptions gracefully with user-friendly messages
- Use logging instead of print statements

### Streamlit Best Practices
- Use session state for data persistence
- Implement caching with @st.cache_data for expensive operations
- Organize UI in logical sections with st.columns and st.container
- Provide helpful tooltips and instructions
- Show spinners for long-running operations

## Key Functions to Implement

### 1. File Handler
```python
def load_dataset(file) -> pd.DataFrame:
    """Load CSV or Excel file into DataFrame"""

def validate_file(file) -> bool:
    """Validate file format and size"""
```

### 2. Matcher
```python
def fuzzy_match(source_val: str, target_val: str, threshold: float = 80.0) -> tuple[float, bool]:
    """Calculate fuzzy match percentage"""

def match_datasets(source_df: pd.DataFrame, target_df: pd.DataFrame,
                   column_mapping: dict, threshold: float) -> pd.DataFrame:
    """Match entire datasets based on mapped columns"""
```

### 3. Exporter
```python
def export_to_excel(source_df: pd.DataFrame, target_df: pd.DataFrame,
                    results_df: pd.DataFrame, filename: str) -> bytes:
    """Export results to Excel with multiple sheets"""
```

## Error Handling

Always handle these common scenarios:
1. Empty files or datasets
2. Mismatched column types
3. Special characters in data
4. Large files causing memory issues
5. Network issues during file upload
6. Invalid Excel formats

## Testing Scenarios

Test with:
1. Small datasets (< 100 rows)
2. Medium datasets (1,000 - 10,000 rows)
3. Large datasets (> 10,000 rows)
4. Mixed data types (strings, numbers, dates)
5. Special characters and unicode
6. Missing/null values
7. Duplicate records

## Performance Optimization

1. Use vectorized pandas operations instead of loops
2. Implement chunking for large files
3. Cache processed data using Streamlit's session state
4. Use multiprocessing for matching large datasets
5. Optimize fuzzy matching with pre-filtering

## UI/UX Considerations

1. Provide clear instructions at each step
2. Show data previews (first 5-10 rows)
3. Display match statistics (total matches, match rate, etc.)
4. Use color coding for match quality (green for high, yellow for medium, red for low)
5. Include a help section with examples
6. Add data validation warnings

## Dependencies to Install

```bash
pip install streamlit pandas numpy openpyxl xlsxwriter fuzzywuzzy python-Levenshtein jellyfish plotly
```

## Success Criteria

The tool is successful when it can:
1. Load and process various file formats without errors
2. Provide accurate matching results with configurable thresholds
3. Export clean, well-formatted Excel files
4. Handle datasets up to 100,000 rows efficiently
5. Provide a smooth, intuitive user experience
