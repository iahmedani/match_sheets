# Changelog

All notable changes to the Dataset Comparison Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-06

### Added

#### Core Features
- **Dataset Matching Tool**: Fuzzy matching comparison between two datasets
  - Multiple matching algorithms (Fuzzy, Token Sort, Token Set, Phonetic)
  - Configurable match threshold (0-100%)
  - Auto-suggest column mappings based on similarity
  - Parallel processing support for large datasets
  - Color-coded match results (Green/Yellow/Red)
  - Comprehensive match statistics (exact matches, fuzzy matches, no matches, match rate)

- **File Concatenation Tool**: Merge multiple CSV/Excel files
  - Upload unlimited files simultaneously
  - Automatic source tracking column
  - Customizable source column name
  - Filter preview by source file
  - Summary statistics per file
  - Export as Excel or CSV

#### User Interface
- Multi-page navigation with sidebar
- Modern, responsive Streamlit interface
- Real-time progress indicators
- Interactive data previews
- File upload with drag-and-drop
- Expandable sections for detailed information
- Contextual help text and tooltips

#### File Support
- CSV file support with multiple encodings (UTF-8, Latin-1, ISO-8859-1)
- Excel file support (.xlsx, .xls)
- File validation (format, size, content)
- Support for files up to 100MB
- Automatic NaN/Inf value handling

#### Export Features
- **Match Results Excel Export** with 4 sheets:
  - `source`: Original source dataset
  - `target`: Original target dataset
  - `match_result`: Detailed match analysis with scores
  - `complete_data`: Source records with matched target columns side-by-side
- **Concatenated Data Export**:
  - Excel format with formatting
  - CSV format
  - Preserved data integrity

#### Data Processing
- Smart column mapping with fuzzy name matching
- Composite key matching (multiple columns)
- Robust error handling and validation
- Memory-efficient processing
- Column-level match scoring

### Technical Implementation
- Modular architecture with separate concerns
- Type hints throughout codebase
- Comprehensive logging
- Session state management
- Clean code following PEP 8
- Error handling with user-friendly messages

### Documentation
- Complete README with usage instructions
- Step-by-step guides for both tools
- API reference for all modules
- Inline code documentation
- Sample datasets included
- Troubleshooting guide

### Testing
- Unit tests for matcher module
- Unit tests for file handler module
- Sample data for testing
- Validation for edge cases

### Dependencies
- streamlit >= 1.28.0
- pandas >= 2.0.0
- numpy >= 1.24.0
- fuzzywuzzy >= 0.18.0
- python-Levenshtein >= 0.21.0
- jellyfish >= 1.0.0
- openpyxl >= 3.1.0
- xlsxwriter >= 3.1.0
- plotly >= 5.17.0

## Commit History

### [2e000d1] - Add file concatenation feature with multi-page navigation
- Multi-page architecture with sidebar navigation
- File concatenation tool
- Source tracking for merged files
- Preview and filter capabilities

### [7b6ba45] - Add complete_data sheet to Excel export
- New sheet combining source and matched target data
- Side-by-side view for easy review
- Color-coded rows based on match quality

### [e384d19] - Fix Excel export error with NaN/Inf values
- Handle NaN and Infinity values in Excel export
- Clean data before export
- Added nan_inf_to_errors option

### [2759294] - Initial implementation of Dataset Comparison Tool
- Core matching functionality
- File handlers for CSV/Excel
- Fuzzy matching algorithms
- Column mapping
- Excel export with 3 sheets
- Streamlit UI
- Sample data

## Future Enhancements (Planned)

- Advanced filtering options
- Custom matching algorithms
- Batch processing
- API endpoint support
- Database connectivity
- More export formats (JSON, Parquet)
- Data visualization charts
- Match confidence analysis
- Deduplication tools
- Schedule automated matching

---

**Full Changelog**: https://github.com/iahmedani/match_sheets/compare/initial...v1.0.0
