"""Main Streamlit application for Dataset Comparison Tool"""

import streamlit as st
import pandas as pd
from src.file_handler import FileHandler
from src.matcher import DataMatcher
from src.mapper import ColumnMapper
from src.exporter import ExcelExporter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Dataset Comparison Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4472C4;
        text-align: center;
        padding: 1rem 0;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2E75B6;
        padding: 0.5rem 0;
        border-bottom: 2px solid #4472C4;
        margin-top: 1rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #F0F8FF;
        border-left: 4px solid #4472C4;
        margin: 1rem 0;
    }
    .metric-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #FFFFFF;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'source_df' not in st.session_state:
        st.session_state.source_df = None
    if 'target_df' not in st.session_state:
        st.session_state.target_df = None
    if 'column_mapping' not in st.session_state:
        st.session_state.column_mapping = {}
    if 'match_results' not in st.session_state:
        st.session_state.match_results = None
    if 'match_stats' not in st.session_state:
        st.session_state.match_stats = None


def render_header():
    """Render the application header"""
    st.markdown('<div class="main-header">🔍 Dataset Comparison Tool</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
    Compare two datasets using intelligent fuzzy matching algorithms. Upload your source and target files,
    map the columns you want to compare, and get detailed match results with exportable Excel reports.
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with configuration options"""
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Match threshold
        threshold = st.slider(
            "Match Threshold (%)",
            min_value=0,
            max_value=100,
            value=80,
            step=5,
            help="Minimum similarity percentage to consider a match"
        )

        # Matching strategy
        strategy = st.selectbox(
            "Matching Strategy",
            options=[
                DataMatcher.FUZZY,
                DataMatcher.TOKEN_SORT,
                DataMatcher.TOKEN_SET,
                DataMatcher.PHONETIC
            ],
            format_func=lambda x: x.replace('_', ' ').title(),
            help="Algorithm to use for fuzzy matching"
        )

        # Parallel processing
        use_parallel = st.checkbox(
            "Use Parallel Processing",
            value=True,
            help="Enable parallel processing for large datasets (>100 rows)"
        )

        st.markdown("---")

        # Help section
        with st.expander("ℹ️ Help & Instructions"):
            st.markdown("""
            ### How to Use:
            1. **Upload Files**: Upload both source and target datasets (CSV or XLSX)
            2. **Map Columns**: Select which columns to compare from each dataset
            3. **Configure**: Adjust match threshold and strategy as needed
            4. **Run Matching**: Click the 'Run Matching' button
            5. **Review Results**: View match statistics and preview results
            6. **Export**: Download the complete results as an Excel file

            ### Matching Strategies:
            - **Fuzzy**: General purpose string matching (recommended)
            - **Token Sort**: Best for reordered words (e.g., "John Doe" vs "Doe John")
            - **Token Set**: Best for partial matches with extra words
            - **Phonetic**: Best for names that sound similar

            ### Match Threshold:
            - Higher threshold (90-100%): More strict, fewer matches
            - Medium threshold (70-85%): Balanced approach
            - Lower threshold (50-70%): More lenient, more matches
            """)

        return threshold, strategy, use_parallel


def render_file_upload_section():
    """Render the file upload section"""
    st.markdown('<div class="section-header">📁 File Upload</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Source Dataset")
        source_file = st.file_uploader(
            "Upload source file",
            type=['csv', 'xlsx', 'xls'],
            key='source_uploader',
            help="Upload the dataset you want to match from"
        )

        if source_file is not None:
            with st.spinner("Loading source file..."):
                df, error = FileHandler.load_dataset(source_file)

                if error:
                    st.error(f"❌ Error loading source file: {error}")
                    st.session_state.source_df = None
                else:
                    st.session_state.source_df = df
                    st.success(f"✅ Loaded {len(df)} rows and {len(df.columns)} columns")

                    with st.expander("Preview Source Data"):
                        st.dataframe(df.head(10), use_container_width=True)

                    # File info
                    file_info = FileHandler.get_file_info(df)
                    with st.expander("Source File Info"):
                        st.json({
                            'Rows': file_info['rows'],
                            'Columns': file_info['columns'],
                            'Memory Usage (MB)': round(file_info['memory_usage'], 2)
                        })

    with col2:
        st.subheader("Target Dataset")
        target_file = st.file_uploader(
            "Upload target file",
            type=['csv', 'xlsx', 'xls'],
            key='target_uploader',
            help="Upload the dataset you want to match against"
        )

        if target_file is not None:
            with st.spinner("Loading target file..."):
                df, error = FileHandler.load_dataset(target_file)

                if error:
                    st.error(f"❌ Error loading target file: {error}")
                    st.session_state.target_df = None
                else:
                    st.session_state.target_df = df
                    st.success(f"✅ Loaded {len(df)} rows and {len(df.columns)} columns")

                    with st.expander("Preview Target Data"):
                        st.dataframe(df.head(10), use_container_width=True)

                    # File info
                    file_info = FileHandler.get_file_info(df)
                    with st.expander("Target File Info"):
                        st.json({
                            'Rows': file_info['rows'],
                            'Columns': file_info['columns'],
                            'Memory Usage (MB)': round(file_info['memory_usage'], 2)
                        })


def render_column_mapping_section():
    """Render the column mapping section"""
    if st.session_state.source_df is None or st.session_state.target_df is None:
        st.info("👆 Please upload both source and target files to continue")
        return False

    st.markdown('<div class="section-header">🔗 Column Mapping</div>', unsafe_allow_html=True)

    source_cols = list(st.session_state.source_df.columns)
    target_cols = list(st.session_state.target_df.columns)

    # Auto-suggest mappings button
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔮 Auto-Suggest Mappings", help="Automatically suggest column mappings based on name similarity"):
            suggested = ColumnMapper.suggest_mappings(source_cols, target_cols, threshold=70)
            st.session_state.column_mapping = suggested

            if suggested:
                st.success(f"✅ Suggested {len(suggested)} column mappings")
            else:
                st.warning("⚠️ No automatic mappings found. Please map columns manually.")

    # Number of columns to map
    num_mappings = st.number_input(
        "Number of columns to compare",
        min_value=1,
        max_value=min(len(source_cols), len(target_cols)),
        value=min(3, min(len(source_cols), len(target_cols))),
        help="Select how many column pairs you want to compare"
    )

    # Create column mapping interface
    st.markdown("#### Map Columns")
    st.markdown("Select which columns from the source should match with which columns in the target:")

    mapping = {}
    for i in range(num_mappings):
        col1, col2, col3 = st.columns([2, 1, 2])

        with col1:
            # Pre-select from session state if available
            default_source_idx = 0
            if st.session_state.column_mapping:
                keys = list(st.session_state.column_mapping.keys())
                if i < len(keys) and keys[i] in source_cols:
                    default_source_idx = source_cols.index(keys[i])

            source_col = st.selectbox(
                f"Source Column {i+1}",
                options=source_cols,
                index=default_source_idx,
                key=f"source_col_{i}"
            )

        with col2:
            st.markdown("<div style='text-align: center; padding-top: 1.8rem;'>➡️</div>",
                       unsafe_allow_html=True)

        with col3:
            # Pre-select from session state if available
            default_target_idx = 0
            if st.session_state.column_mapping and source_col in st.session_state.column_mapping:
                target_val = st.session_state.column_mapping[source_col]
                if target_val in target_cols:
                    default_target_idx = target_cols.index(target_val)

            target_col = st.selectbox(
                f"Target Column {i+1}",
                options=target_cols,
                index=default_target_idx,
                key=f"target_col_{i}"
            )

        mapping[source_col] = target_col

        # Show sample values
        with st.expander(f"Preview: {source_col} ↔️ {target_col}"):
            preview_col1, preview_col2 = st.columns(2)
            with preview_col1:
                st.markdown(f"**Source ({source_col}):**")
                st.write(st.session_state.source_df[source_col].head(5).tolist())
            with preview_col2:
                st.markdown(f"**Target ({target_col}):**")
                st.write(st.session_state.target_df[target_col].head(5).tolist())

    st.session_state.column_mapping = mapping

    # Validate mapping
    is_valid, errors = ColumnMapper.validate_mapping(
        mapping,
        st.session_state.source_df,
        st.session_state.target_df
    )

    if not is_valid:
        st.error("❌ Invalid column mapping:")
        for error in errors:
            st.error(f"  • {error}")
        return False

    return True


def render_matching_section(threshold: float, strategy: str, use_parallel: bool):
    """Render the matching execution section"""
    if not st.session_state.column_mapping:
        return

    st.markdown('<div class="section-header">🎯 Run Matching</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        run_button = st.button(
            "▶️ Run Matching",
            type="primary",
            use_container_width=True,
            help="Start the matching process"
        )

    if run_button:
        with st.spinner("🔄 Matching datasets... This may take a moment for large datasets."):
            try:
                # Initialize matcher
                matcher = DataMatcher(threshold=threshold)

                # Perform matching
                results_df = matcher.match_datasets(
                    st.session_state.source_df,
                    st.session_state.target_df,
                    st.session_state.column_mapping,
                    strategy=strategy,
                    use_parallel=use_parallel
                )

                # Calculate statistics
                stats = DataMatcher.get_match_statistics(results_df)

                # Store in session state
                st.session_state.match_results = results_df
                st.session_state.match_stats = stats

                st.success("✅ Matching completed successfully!")

            except Exception as e:
                logger.error(f"Error during matching: {str(e)}")
                st.error(f"❌ Error during matching: {str(e)}")


def render_results_section():
    """Render the results section"""
    if st.session_state.match_results is None:
        return

    st.markdown('<div class="section-header">📊 Match Results</div>', unsafe_allow_html=True)

    # Display statistics
    stats = st.session_state.match_stats

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Rows", stats['total_rows'])

    with col2:
        st.metric("Exact Matches", stats['exact_matches'])

    with col3:
        st.metric("Fuzzy Matches", stats['fuzzy_matches'])

    with col4:
        st.metric("No Matches", stats['no_matches'])

    with col5:
        st.metric("Match Rate", f"{stats['match_rate']}%")

    # Additional metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Average Match Score", f"{stats['avg_match_score']}%")

    # Results preview
    st.markdown("#### Results Preview")

    # Filter options
    filter_col1, filter_col2 = st.columns([3, 1])

    with filter_col1:
        filter_option = st.selectbox(
            "Filter results",
            options=['All Results', 'Exact Matches Only', 'Fuzzy Matches Only', 'No Matches Only'],
            help="Filter the results table"
        )

    # Apply filter
    filtered_results = st.session_state.match_results.copy()

    if filter_option == 'Exact Matches Only':
        filtered_results = filtered_results[filtered_results['match_status'] == 'exact']
    elif filter_option == 'Fuzzy Matches Only':
        filtered_results = filtered_results[filtered_results['match_status'] == 'fuzzy']
    elif filter_option == 'No Matches Only':
        filtered_results = filtered_results[filtered_results['match_status'] == 'no_match']

    # Display results table
    st.dataframe(
        filtered_results,
        use_container_width=True,
        height=400
    )

    st.info(f"Showing {len(filtered_results)} of {len(st.session_state.match_results)} results")


def render_export_section():
    """Render the export section"""
    if st.session_state.match_results is None:
        return

    st.markdown('<div class="section-header">💾 Export Results</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        if st.button("📥 Download Excel Report", type="primary", use_container_width=True):
            with st.spinner("Generating Excel file..."):
                try:
                    excel_data = ExcelExporter.export_to_excel(
                        st.session_state.source_df,
                        st.session_state.target_df,
                        st.session_state.match_results,
                        column_mapping=st.session_state.column_mapping,
                        filename="match_results.xlsx"
                    )

                    st.download_button(
                        label="💾 Download match_results.xlsx",
                        data=excel_data,
                        file_name="match_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        use_container_width=True
                    )

                    st.success("✅ Excel file ready for download!")

                except Exception as e:
                    logger.error(f"Error exporting to Excel: {str(e)}")
                    st.error(f"❌ Error exporting to Excel: {str(e)}")

    st.markdown("""
    <div class="info-box">
    <strong>Excel Export includes:</strong>
    <ul>
        <li><strong>source</strong> sheet: Original source dataset</li>
        <li><strong>target</strong> sheet: Original target dataset</li>
        <li><strong>match_result</strong> sheet: Detailed match results with color coding</li>
        <li><strong>complete_data</strong> sheet: All source records with matched target columns side-by-side</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()

    # Render header
    render_header()

    # Render sidebar and get configuration
    threshold, strategy, use_parallel = render_sidebar()

    # Render main sections
    render_file_upload_section()

    mapping_valid = render_column_mapping_section()

    if mapping_valid:
        render_matching_section(threshold, strategy, use_parallel)

    render_results_section()

    render_export_section()

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>Dataset Comparison Tool v1.0.0 | "
        "Built with Streamlit 🎈</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
