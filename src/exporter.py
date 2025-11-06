"""Excel export functionality for match results"""

import pandas as pd
import numpy as np
import io
from typing import Optional
import logging
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExcelExporter:
    """Handles exporting match results to Excel format"""

    # Color schemes for match quality
    EXACT_MATCH_COLOR = "C6EFCE"  # Light green
    FUZZY_MATCH_COLOR = "FFEB9C"  # Light yellow
    NO_MATCH_COLOR = "FFC7CE"     # Light red
    HEADER_COLOR = "4472C4"       # Blue

    @staticmethod
    def export_to_excel(source_df: pd.DataFrame, target_df: pd.DataFrame,
                       results_df: pd.DataFrame, column_mapping: dict = None,
                       filename: str = "match_results.xlsx") -> bytes:
        """
        Export datasets and match results to Excel with multiple sheets

        Args:
            source_df: Original source DataFrame
            target_df: Original target DataFrame
            results_df: Match results DataFrame
            column_mapping: Dictionary mapping source columns to target columns
            filename: Name for the Excel file

        Returns:
            Bytes of the Excel file
        """
        logger.info(f"Exporting results to Excel: {filename}")

        # Clean DataFrames - replace NaN/Inf values
        source_df_clean = source_df.copy()
        target_df_clean = target_df.copy()
        results_df_clean = results_df.copy()

        # Replace NaN and Inf with None (which Excel handles as empty cells)
        source_df_clean = source_df_clean.replace([np.inf, -np.inf], None)
        target_df_clean = target_df_clean.replace([np.inf, -np.inf], None)
        results_df_clean = results_df_clean.replace([np.inf, -np.inf], None)

        # Fill NaN with None
        source_df_clean = source_df_clean.where(pd.notna(source_df_clean), None)
        target_df_clean = target_df_clean.where(pd.notna(target_df_clean), None)
        results_df_clean = results_df_clean.where(pd.notna(results_df_clean), None)

        # Create complete_data sheet: source + matched target columns
        complete_data_df = ExcelExporter._create_complete_data(
            source_df_clean,
            target_df_clean,
            results_df_clean,
            column_mapping
        )

        # Create a BytesIO buffer
        output = io.BytesIO()

        # Create Excel writer with xlsxwriter engine and nan_inf_to_errors option
        with pd.ExcelWriter(output, engine='xlsxwriter',
                          engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
            # Write source data (cleaned)
            source_df_clean.to_excel(writer, sheet_name='source', index=False)

            # Write target data (cleaned)
            target_df_clean.to_excel(writer, sheet_name='target', index=False)

            # Write match results (cleaned)
            results_df_clean.to_excel(writer, sheet_name='match_result', index=False)

            # Write complete data sheet
            if complete_data_df is not None:
                complete_data_df.to_excel(writer, sheet_name='complete_data', index=False)

            # Get workbook and worksheets for formatting
            workbook = writer.book

            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4472C4',
                'font_color': 'white',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            })

            exact_match_format = workbook.add_format({
                'bg_color': ExcelExporter.EXACT_MATCH_COLOR,
                'border': 1
            })

            fuzzy_match_format = workbook.add_format({
                'bg_color': ExcelExporter.FUZZY_MATCH_COLOR,
                'border': 1
            })

            no_match_format = workbook.add_format({
                'bg_color': ExcelExporter.NO_MATCH_COLOR,
                'border': 1
            })

            percentage_format = workbook.add_format({
                'num_format': '0.00',
                'border': 1
            })

            # Format each worksheet (use cleaned dataframes)
            ExcelExporter._format_worksheet(writer.sheets['source'], source_df_clean, header_format)
            ExcelExporter._format_worksheet(writer.sheets['target'], target_df_clean, header_format)
            ExcelExporter._format_match_results(
                writer.sheets['match_result'],
                results_df_clean,
                header_format,
                exact_match_format,
                fuzzy_match_format,
                no_match_format,
                percentage_format
            )

            # Format complete_data sheet
            if complete_data_df is not None:
                ExcelExporter._format_complete_data(
                    writer.sheets['complete_data'],
                    complete_data_df,
                    header_format,
                    exact_match_format,
                    fuzzy_match_format,
                    no_match_format
                )

        output.seek(0)
        logger.info("Excel export completed successfully")
        return output.getvalue()

    @staticmethod
    def _format_worksheet(worksheet, df: pd.DataFrame, header_format):
        """Apply formatting to a standard worksheet"""
        # Format headers
        for col_num, column in enumerate(df.columns):
            worksheet.write(0, col_num, column, header_format)

        # Auto-adjust column widths
        for col_num, column in enumerate(df.columns):
            max_length = max(
                df[column].astype(str).apply(len).max(),
                len(str(column))
            )
            # Add some padding
            worksheet.set_column(col_num, col_num, min(max_length + 2, 50))

        # Freeze the header row
        worksheet.freeze_panes(1, 0)

    @staticmethod
    def _format_match_results(worksheet, df: pd.DataFrame, header_format,
                             exact_match_format, fuzzy_match_format,
                             no_match_format, percentage_format):
        """Apply conditional formatting to match results worksheet"""
        # Format headers
        for col_num, column in enumerate(df.columns):
            worksheet.write(0, col_num, column, header_format)

        # Find the match_status and match_percentage columns
        status_col_idx = df.columns.get_loc('match_status') if 'match_status' in df.columns else None
        percentage_col_idx = df.columns.get_loc('match_percentage') if 'match_percentage' in df.columns else None

        # Apply conditional formatting based on match status
        for row_num, row in df.iterrows():
            excel_row = row_num + 1  # Excel rows are 1-indexed, +1 for header

            match_status = row.get('match_status', 'no_match')

            # Select the appropriate format
            if match_status == 'exact':
                row_format = exact_match_format
            elif match_status == 'fuzzy':
                row_format = fuzzy_match_format
            else:
                row_format = no_match_format

            # Apply format to the entire row
            for col_num, value in enumerate(row):
                # Use percentage format for match_percentage column
                if col_num == percentage_col_idx:
                    worksheet.write(excel_row, col_num, value, percentage_format)
                else:
                    worksheet.write(excel_row, col_num, value, row_format)

        # Auto-adjust column widths
        for col_num, column in enumerate(df.columns):
            max_length = max(
                df[column].astype(str).apply(len).max(),
                len(str(column))
            )
            worksheet.set_column(col_num, col_num, min(max_length + 2, 50))

        # Freeze the header row
        worksheet.freeze_panes(1, 0)

    @staticmethod
    def _create_complete_data(source_df: pd.DataFrame, target_df: pd.DataFrame,
                             results_df: pd.DataFrame, column_mapping: dict) -> pd.DataFrame:
        """
        Create a complete data DataFrame combining source and matched target columns

        Args:
            source_df: Source DataFrame
            target_df: Target DataFrame
            results_df: Match results DataFrame
            column_mapping: Dictionary mapping source columns to target columns

        Returns:
            Complete data DataFrame or None if column_mapping is not provided
        """
        if column_mapping is None or len(column_mapping) == 0:
            logger.warning("No column mapping provided, skipping complete_data sheet")
            return None

        try:
            # Start with all source columns
            complete_df = source_df.copy()

            # Add match status and percentage from results
            if 'match_status' in results_df.columns:
                complete_df['match_status'] = results_df['match_status'].values
            if 'match_percentage' in results_df.columns:
                complete_df['match_percentage'] = results_df['match_percentage'].values

            # For each target column that was mapped, add it to complete data
            target_cols = list(column_mapping.values())

            for target_col in set(target_cols):  # Use set to avoid duplicates
                # Find the corresponding data from results_df
                result_col_name = f'target_{target_col}'
                if result_col_name in results_df.columns:
                    complete_df[f'matched_{target_col}'] = results_df[result_col_name].values
                else:
                    # If not in results, try to get from target_df using target_index
                    if 'target_index' in results_df.columns:
                        matched_values = []
                        for idx in results_df['target_index']:
                            if pd.notna(idx) and int(idx) < len(target_df):
                                matched_values.append(target_df.iloc[int(idx)][target_col])
                            else:
                                matched_values.append(None)
                        complete_df[f'matched_{target_col}'] = matched_values

            logger.info(f"Created complete_data sheet with {len(complete_df)} rows and {len(complete_df.columns)} columns")
            return complete_df

        except Exception as e:
            logger.error(f"Error creating complete_data sheet: {str(e)}")
            return None

    @staticmethod
    def _format_complete_data(worksheet, df: pd.DataFrame, header_format,
                             exact_match_format, fuzzy_match_format, no_match_format):
        """Apply formatting to complete data worksheet"""
        # Format headers
        for col_num, column in enumerate(df.columns):
            worksheet.write(0, col_num, column, header_format)

        # Find the match_status column
        status_col_idx = df.columns.get_loc('match_status') if 'match_status' in df.columns else None

        # Apply conditional formatting based on match status
        for row_num, row in df.iterrows():
            excel_row = row_num + 1  # Excel rows are 1-indexed, +1 for header

            match_status = row.get('match_status', 'no_match')

            # Select the appropriate format
            if match_status == 'exact':
                row_format = exact_match_format
            elif match_status == 'fuzzy':
                row_format = fuzzy_match_format
            else:
                row_format = no_match_format

            # Apply format to the entire row
            for col_num, value in enumerate(row):
                worksheet.write(excel_row, col_num, value, row_format)

        # Auto-adjust column widths
        for col_num, column in enumerate(df.columns):
            max_length = max(
                df[column].astype(str).apply(len).max(),
                len(str(column))
            )
            worksheet.set_column(col_num, col_num, min(max_length + 2, 50))

        # Freeze the header row
        worksheet.freeze_panes(1, 0)

    @staticmethod
    def export_to_excel_openpyxl(source_df: pd.DataFrame, target_df: pd.DataFrame,
                                  results_df: pd.DataFrame) -> bytes:
        """
        Alternative export method using openpyxl for more advanced formatting

        Args:
            source_df: Original source DataFrame
            target_df: Original target DataFrame
            results_df: Match results DataFrame

        Returns:
            Bytes of the Excel file
        """
        # Clean DataFrames - replace NaN/Inf values
        source_df_clean = source_df.copy()
        target_df_clean = target_df.copy()
        results_df_clean = results_df.copy()

        # Replace NaN and Inf with None
        source_df_clean = source_df_clean.replace([np.inf, -np.inf], None)
        target_df_clean = target_df_clean.replace([np.inf, -np.inf], None)
        results_df_clean = results_df_clean.replace([np.inf, -np.inf], None)

        # Fill NaN with None
        source_df_clean = source_df_clean.where(pd.notna(source_df_clean), None)
        target_df_clean = target_df_clean.where(pd.notna(target_df_clean), None)
        results_df_clean = results_df_clean.where(pd.notna(results_df_clean), None)

        output = io.BytesIO()

        # Create Excel file with pandas
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            source_df_clean.to_excel(writer, sheet_name='source', index=False)
            target_df_clean.to_excel(writer, sheet_name='target', index=False)
            results_df_clean.to_excel(writer, sheet_name='match_result', index=False)

        # Reload with openpyxl for advanced formatting
        output.seek(0)
        wb = load_workbook(output)

        # Define styles
        header_fill = PatternFill(start_color=ExcelExporter.HEADER_COLOR.replace('#', ''),
                                  end_color=ExcelExporter.HEADER_COLOR.replace('#', ''),
                                  fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF')

        exact_fill = PatternFill(start_color=ExcelExporter.EXACT_MATCH_COLOR,
                                end_color=ExcelExporter.EXACT_MATCH_COLOR,
                                fill_type='solid')

        fuzzy_fill = PatternFill(start_color=ExcelExporter.FUZZY_MATCH_COLOR,
                                end_color=ExcelExporter.FUZZY_MATCH_COLOR,
                                fill_type='solid')

        no_match_fill = PatternFill(start_color=ExcelExporter.NO_MATCH_COLOR,
                                    end_color=ExcelExporter.NO_MATCH_COLOR,
                                    fill_type='solid')

        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Format match_result sheet with conditional coloring
        ws = wb['match_result']

        # Format headers
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = thin_border

        # Find match_status column
        status_col = None
        for idx, cell in enumerate(ws[1], 1):
            if cell.value == 'match_status':
                status_col = idx
                break

        # Apply conditional formatting
        if status_col:
            for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                status_value = row[status_col - 1].value

                if status_value == 'exact':
                    fill = exact_fill
                elif status_value == 'fuzzy':
                    fill = fuzzy_fill
                else:
                    fill = no_match_fill

                for cell in row:
                    cell.fill = fill
                    cell.border = thin_border

        # Auto-adjust column widths for all sheets
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            for column in ws.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)

                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass

                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width

            # Freeze header row
            ws.freeze_panes = 'A2'

        # Save to BytesIO
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        return output.getvalue()
