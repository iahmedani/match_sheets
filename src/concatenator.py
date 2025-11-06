"""File concatenation functionality"""

import pandas as pd
import numpy as np
from typing import List, Tuple
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileConcatenator:
    """Handles concatenation of multiple CSV/Excel files"""

    @staticmethod
    def concatenate_files(files: List, include_source: bool = True) -> Tuple[pd.DataFrame, List[str]]:
        """
        Concatenate multiple CSV/Excel files into a single DataFrame

        Args:
            files: List of uploaded file objects
            include_source: Whether to include a 'source' column with filename

        Returns:
            Tuple of (concatenated DataFrame, list of errors)
        """
        if not files or len(files) == 0:
            return None, ["No files provided"]

        dataframes = []
        errors = []

        for file in files:
            try:
                # Get filename without extension
                filename = os.path.splitext(file.name)[0]

                # Load the file
                if file.name.lower().endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.lower().endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file)
                else:
                    errors.append(f"Unsupported file format: {file.name}")
                    continue

                if df.empty:
                    errors.append(f"File is empty: {file.name}")
                    continue

                # Add source column if requested
                if include_source:
                    df['source'] = filename

                dataframes.append(df)
                logger.info(f"Loaded {file.name}: {len(df)} rows, {len(df.columns)} columns")

            except Exception as e:
                errors.append(f"Error loading {file.name}: {str(e)}")
                logger.error(f"Error loading {file.name}: {str(e)}")

        if not dataframes:
            return None, errors if errors else ["No valid files to concatenate"]

        try:
            # Concatenate all dataframes
            concatenated_df = pd.concat(dataframes, ignore_index=True, sort=False)

            logger.info(f"Successfully concatenated {len(dataframes)} files into {len(concatenated_df)} rows")

            return concatenated_df, errors

        except Exception as e:
            error_msg = f"Error concatenating files: {str(e)}"
            logger.error(error_msg)
            return None, [error_msg]

    @staticmethod
    def get_concatenation_summary(df: pd.DataFrame, source_col: str = 'source') -> dict:
        """
        Get summary statistics about the concatenated data

        Args:
            df: Concatenated DataFrame
            source_col: Name of the source column

        Returns:
            Dictionary with summary statistics
        """
        if df is None or df.empty:
            return {}

        summary = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
        }

        # If source column exists, get counts by source
        if source_col in df.columns:
            summary['rows_by_source'] = df[source_col].value_counts().to_dict()
            summary['source_files'] = df[source_col].unique().tolist()
            summary['number_of_files'] = df[source_col].nunique()

        return summary

    @staticmethod
    def export_concatenated_data(df: pd.DataFrame, format: str = 'xlsx') -> bytes:
        """
        Export concatenated data to Excel or CSV

        Args:
            df: DataFrame to export
            format: Output format ('xlsx' or 'csv')

        Returns:
            Bytes of the exported file
        """
        import io

        if df is None or df.empty:
            raise ValueError("No data to export")

        # Clean DataFrame - replace NaN/Inf values
        df_clean = df.copy()
        df_clean = df_clean.replace([np.inf, -np.inf], None)
        df_clean = df_clean.where(pd.notna(df_clean), None)

        if format.lower() == 'xlsx':
            output = io.BytesIO()

            with pd.ExcelWriter(output, engine='xlsxwriter',
                              engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
                df_clean.to_excel(writer, sheet_name='concatenated_data', index=False)

                # Get workbook and worksheet for formatting
                workbook = writer.book
                worksheet = writer.sheets['concatenated_data']

                # Define header format
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#4472C4',
                    'font_color': 'white',
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter'
                })

                # Format headers
                for col_num, column in enumerate(df_clean.columns):
                    worksheet.write(0, col_num, column, header_format)

                # Auto-adjust column widths
                for col_num, column in enumerate(df_clean.columns):
                    max_length = max(
                        df_clean[column].astype(str).apply(len).max(),
                        len(str(column))
                    )
                    worksheet.set_column(col_num, col_num, min(max_length + 2, 50))

                # Freeze the header row
                worksheet.freeze_panes(1, 0)

            output.seek(0)
            return output.getvalue()

        elif format.lower() == 'csv':
            output = io.StringIO()
            df_clean.to_csv(output, index=False)
            return output.getvalue().encode('utf-8')

        else:
            raise ValueError(f"Unsupported export format: {format}")
