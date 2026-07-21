"""
Module 9: Export Dataset
Export cleaned dataset to CSV and generate cleaning report.
"""

import os
import pandas as pd
from datetime import datetime

class DataExporter:
    """Handles exporting cleaned data and reports."""

    @staticmethod
    def export_csv(df: pd.DataFrame, filename: str = "cleaned_dataset.csv", output_dir: str = "data/") -> str:
        """Export DataFrame to CSV."""
        os.makedirs(output_dir, exist_ok=True)
        # Ensure output path
        if not filename.endswith(".csv"):
            filename += ".csv"
        
        # If output_dir is part of filename, respect it
        if os.path.dirname(filename):
            full_path = filename
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
        else:
            full_path = os.path.join(output_dir, filename)

        # For datetime columns, ensure ISO format YYYY-MM-DD if not already
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime("%Y-%m-%d")

        df.to_csv(full_path, index=False)
        print(f"[Exporter] Cleaned Dataset Saved")
        print(f"[Exporter] File Name: {full_path}")
        print(f"[Exporter] Rows: {df.shape[0]}, Columns: {df.shape[1]}")
        return full_path

    @staticmethod
    def generate_cleaning_report(original_info: dict, cleaning_log: dict, 
                                 final_df: pd.DataFrame, validation_result: dict,
                                 report_path: str = "reports/cleaning_report.txt"):
        """Generate comprehensive report per Module 10."""
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Calculate metrics
        original_rows = original_info.get("rows", 0)
        original_cols = original_info.get("columns", 0)
        final_rows = final_df.shape[0]
        final_cols = final_df.shape[1]
        remaining_nulls = validation_result.get("remaining_nulls", final_df.isnull().sum().sum())

        report_content = f"""
================================================================================
DATA CLEANING & PREPROCESSING REPORT
================================================================================
Generated On: {timestamp}
Tool Version: 1.0

--------------------------------------------------------------------------------
ORIGINAL DATASET
--------------------------------------------------------------------------------
- Total Rows: {original_rows}
- Total Columns: {original_cols}
- Shape: {original_info.get('shape')}
- Memory Usage: {original_info.get('memory_usage_mb')} MB
- Column Names: {', '.join(original_info.get('column_names', []))}

Data Types (Original):
"""
        for col, dtype in original_info.get("dtypes", {}).items():
            report_content += f"  - {col}: {dtype}\n"

        report_content += f"""
--------------------------------------------------------------------------------
CLEANING SUMMARY
--------------------------------------------------------------------------------
- Missing Values Fixed: {cleaning_log.get('missing_values_fixed', 0)}
- Duplicates Removed: {cleaning_log.get('duplicates_removed', 0)}
- Data Types Corrected: {cleaning_log.get('data_types_corrected', 0)}
- String Cleaning Operations: {cleaning_log.get('string_cleaning_ops', 0)}
- Numeric Cleaning Operations: {cleaning_log.get('numeric_cleaning_ops', 0)}
- Date Formatting Operations: {cleaning_log.get('date_formatting_ops', 0)}

Missing Values Handling:
  Strategy Used: {cleaning_log.get('missing_strategy', 'auto')}
  
Duplicate Handling:
  Strategy Used: Keep={cleaning_log.get('dedup_keep', 'first')}

String Cleaning:
  - Extra spaces removed
  - Inconsistent casing handled (trimmed)
  - Special characters check performed

Date Formatting:
  - Mixed formats converted to YYYY-MM-DD
  Example: 12-04-24 -> 2024-04-12

Numeric Cleaning:
  - Commas removed (e.g., 1,000 -> 1000)
  - Currency symbols removed (e.g., $500, ₹1000 -> 500, 1000)
  - Negative values handled

--------------------------------------------------------------------------------
FINAL DATASET
--------------------------------------------------------------------------------
- Rows: {final_rows}
- Columns: {final_cols}
- Remaining Null Values: {remaining_nulls}
- Remaining Duplicates: {validation_result.get('remaining_duplicates', 0)}
- Validation Status: {validation_result.get('status', 'Unknown')}

Column-wise Remaining Nulls:
"""
        for col, null_count in final_df.isnull().sum().items():
            report_content += f"  - {col}: {null_count}\n"

        report_content += f"""
Final Data Types:
"""
        for col, dtype in final_df.dtypes.items():
            report_content += f"  - {col}: {dtype}\n"

        report_content += f"""
Sample Cleaned Data (Top 5 Rows):
{final_df.head().to_string()}

--------------------------------------------------------------------------------
VALIDATION CHECKS
--------------------------------------------------------------------------------
Missing Values After Cleaning: {validation_result.get('remaining_nulls', 0)} 
  -> {'PASS' if validation_result.get('remaining_nulls', 0) == 0 else 'REVIEW NEEDED'}

Duplicate Records After Cleaning: {validation_result.get('remaining_duplicates', 0)}
  -> {'PASS' if validation_result.get('remaining_duplicates', 0) == 0 else 'REVIEW NEEDED'}

Invalid Data Types After Cleaning: {len(validation_result.get('invalid_types', {}))}
  -> {'PASS' if len(validation_result.get('invalid_types', {})) == 0 else 'ISSUES FOUND'}

Overall Status: {validation_result.get('status', 'Unknown')}

================================================================================
END OF REPORT
================================================================================
"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"[Exporter] Cleaning Report Generated: {report_path}")
        return report_path

    @staticmethod
    def export_excel(df: pd.DataFrame, filename: str = "cleaned_dataset.xlsx", output_dir: str = "data/") -> str:
        """Optional Excel export for future enhancement."""
        os.makedirs(output_dir, exist_ok=True)
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"
        full_path = os.path.join(output_dir, filename)
        df.to_excel(full_path, index=False)
        print(f"[Exporter] Excel Exported: {full_path}")
        return full_path
