# Dataset Comparison Tool

A powerful Python application that compares two datasets using intelligent fuzzy matching algorithms with an intuitive Streamlit web interface.

## Features

- **Multi-format Support**: Upload CSV and Excel (XLSX/XLS) files
- **Intelligent Matching**: Multiple fuzzy matching algorithms including:
  - Levenshtein distance (fuzzy matching)
  - Token-based matching for reordered words
  - Phonetic matching for names
  - Exact matching
- **Interactive UI**: Modern, responsive web interface built with Streamlit
- **Column Mapping**: Auto-suggest or manually map columns between datasets
- **Configurable Thresholds**: Adjust match sensitivity from 0-100%
- **Detailed Results**: Color-coded match results with statistics
- **Excel Export**: Export results with three sheets (source, target, match_result)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd match_sheets
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

Start the Streamlit application:
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Step-by-Step Guide

1. **Upload Files**
   - Upload your source dataset (the dataset you want to match from)
   - Upload your target dataset (the dataset you want to match against)
   - Supported formats: CSV, XLSX, XLS

2. **Map Columns**
   - Click "Auto-Suggest Mappings" for automatic column matching
   - Or manually select which columns to compare
   - Preview sample values from each column

3. **Configure Settings** (Sidebar)
   - **Match Threshold**: Set the minimum similarity percentage (default: 80%)
   - **Matching Strategy**: Choose the algorithm:
     - **Fuzzy**: General purpose (recommended)
     - **Token Sort**: Best for reordered words
     - **Token Set**: Best for partial matches
     - **Phonetic**: Best for similar-sounding names
   - **Parallel Processing**: Enable for faster processing of large datasets

4. **Run Matching**
   - Click "Run Matching" to start the comparison
   - View real-time statistics and results

5. **Export Results**
   - Download the Excel file with complete match results
   - Includes color-coded results:
     - Green: Exact matches
     - Yellow: Fuzzy matches
     - Red: No matches

## Project Structure

```
match_sheets/
├── app.py                      # Main Streamlit application
├── Claude.md                   # Development instructions
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
├── src/
│   ├── __init__.py
│   ├── file_handler.py         # File I/O operations
│   ├── matcher.py              # Matching algorithms
│   ├── mapper.py               # Column mapping logic
│   └── exporter.py             # Excel export functionality
├── utils/
│   └── __init__.py
├── tests/
│   └── (test files)
└── sample_data/
    ├── source_sample.csv       # Sample source dataset
    └── target_sample.csv       # Sample target dataset
```

## Sample Data

The `sample_data/` directory contains example datasets to test the tool:

- **source_sample.csv**: 10 customer records
- **target_sample.csv**: 12 customer records with variations

Try uploading these files to see how the tool handles:
- Reordered names (e.g., "John Smith" vs "Smith John")
- Abbreviated names (e.g., "Jennifer Davis" vs "Jenny Davis")
- Different company name formats (e.g., "Acme Corp" vs "Acme Corporation")

## Matching Algorithms

### Fuzzy Matching (Default)
Uses Levenshtein distance to calculate similarity between strings. Works well for most use cases including typos and minor variations.

### Token Sort Ratio
Tokenizes strings and sorts words before comparing. Excellent for:
- "John Smith" vs "Smith John"
- "New York City" vs "City New York"

### Token Set Ratio
Compares unique tokens between strings. Best for:
- "The Big Company Inc" vs "Big Company"
- Handling extra words or different word orders

### Phonetic Matching
Uses Metaphone algorithm to match words that sound similar. Ideal for:
- Name variations: "Smith" vs "Smyth"
- "Catherine" vs "Katherine"

## Configuration

### Match Threshold

- **90-100%**: Very strict, only near-exact matches
- **80-89%**: Recommended for most use cases
- **70-79%**: More lenient, catches more variations
- **Below 70%**: Very permissive, may include false positives

### Performance Tips

1. **Large Datasets**: Enable parallel processing for datasets over 100 rows
2. **Memory**: The tool supports files up to 100MB
3. **Column Selection**: Focus on key identifier columns for better performance
4. **Strategy**: Use Token Sort or Token Set for structured data with predictable patterns

## API Reference

### FileHandler

```python
from src.file_handler import FileHandler

# Load a dataset
df, error = FileHandler.load_dataset(file, encoding='utf-8')

# Validate a file
is_valid, error_msg = FileHandler.validate_file(file)

# Get file information
info = FileHandler.get_file_info(df)
```

### DataMatcher

```python
from src.matcher import DataMatcher

# Initialize matcher
matcher = DataMatcher(threshold=80.0)

# Match two values
score, match_type = matcher.fuzzy_match(source_val, target_val, strategy='fuzzy')

# Match entire datasets
results_df = matcher.match_datasets(source_df, target_df, column_mapping)

# Get statistics
stats = DataMatcher.get_match_statistics(results_df)
```

### ColumnMapper

```python
from src.mapper import ColumnMapper

# Suggest mappings
suggestions = ColumnMapper.suggest_mappings(source_cols, target_cols, threshold=70)

# Validate mapping
is_valid, errors = ColumnMapper.validate_mapping(mapping, source_df, target_df)
```

### ExcelExporter

```python
from src.exporter import ExcelExporter

# Export to Excel
excel_bytes = ExcelExporter.export_to_excel(source_df, target_df, results_df)
```

## Troubleshooting

### Common Issues

**Problem**: File upload fails
- **Solution**: Check file size (max 100MB) and format (CSV, XLSX, XLS only)

**Problem**: Encoding errors with CSV files
- **Solution**: The tool automatically tries multiple encodings (UTF-8, Latin-1, ISO-8859-1)

**Problem**: Poor match results
- **Solution**: Try adjusting the threshold or switching matching strategies

**Problem**: Slow performance
- **Solution**: Enable parallel processing or reduce the number of columns to compare

### Error Messages

- **"File is empty"**: The uploaded file contains no data
- **"Unsupported file format"**: Use CSV, XLSX, or XLS files only
- **"File size exceeds maximum"**: Reduce file size to under 100MB
- **"Invalid column mapping"**: Check that selected columns exist in both datasets

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

This project follows PEP 8 style guidelines. Format code with:
```bash
black .
flake8 .
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Requirements

- pandas >= 2.0.0
- numpy >= 1.24.0
- streamlit >= 1.28.0
- fuzzywuzzy >= 0.18.0
- python-Levenshtein >= 0.21.0
- jellyfish >= 1.0.0
- openpyxl >= 3.1.0
- xlsxwriter >= 3.1.0
- plotly >= 5.17.0
- python-dotenv >= 1.0.0

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

## Changelog

### Version 1.0.0 (2024)
- Initial release
- Support for CSV and Excel files
- Multiple matching algorithms
- Interactive Streamlit UI
- Excel export with formatting
- Parallel processing support
- Auto-suggest column mappings

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Fuzzy matching powered by [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy)
- Phonetic matching using [Jellyfish](https://github.com/jamesturk/jellyfish)
