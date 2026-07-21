"""
Data Cleaning & Preprocessing Automation Tool
Main Orchestrator - Implements Workflow from PRD:
Start -> Select Dataset -> Load CSV -> Inspect -> Identify Missing -> Detect Duplicates 
-> Validate Data Types -> Clean Dataset -> Preprocess -> Generate Report -> Save -> End
"""

import os
import sys
import pandas as pd

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.loader import DataLoader
from src.inspector import DataInspector
from src.cleaner import DataCleaner
from src.validator import DataValidator
from src.exporter import DataExporter


def run_pipeline(input_file: str = "data/raw_data.csv", 
                 output_file: str = "data/cleaned_data.csv",
                 report_file: str = "reports/cleaning_report.txt",
                 missing_strategy: str = "auto",
                 dedup_keep: str = "first"):
    """Run complete cleaning pipeline as per PRD Workflow."""

    print("\n" + "#"*60)
    print("DATA CLEANING & PREPROCESSING AUTOMATION TOOL v1.0")
    print("#"*60 + "\n")

    # Step 1 & 2: Select Dataset & Load CSV
    print(f"[Workflow] Selecting Dataset: {input_file}")
    try:
        df = DataLoader.load_csv(input_file)
    except Exception as e:
        print(f"[ERROR] Could not load dataset: {e}")
        return None

    print("\nDataset Loaded Successfully")

    # Step 3: Inspect Dataset
    inspector = DataInspector(df)
    original_info = inspector.get_basic_info()
    inspector.display_info()

    print(f"Rows : {original_info['rows']}")
    print(f"Columns : {original_info['columns']}")
    print(f"Shape : {original_info['shape']}")

    # Step 4: Identify Missing Values
    missing_report = inspector.check_missing_values()
    total_missing = df.isnull().sum().sum()
    print(f"Missing Values Found : {total_missing}")

    # Step 5: Detect Duplicates
    dup_info = inspector.check_duplicates()
    print(f"Duplicate Rows Found : {dup_info['total_duplicates']}")

    # Step 6: Validate Data Types
    dtype_issues = inspector.validate_dtypes()
    print(f"Data Types Issues Found : {len(dtype_issues)}")

    inspector.get_summary_stats()

    # Step 7 & 8: Clean Dataset & Preprocess Data
    cleaner = DataCleaner(df)
    cleaned_df = cleaner.full_cleaning_pipeline(
        missing_strategy=missing_strategy,
        dedup_keep=dedup_keep,
        clean_strings=True,
        clean_numeric=True,
        clean_dates=True,
        correct_dtypes=True,
        preprocess=True
    )

    cleaning_log = cleaner.get_cleaning_log()
    cleaning_log["missing_strategy"] = missing_strategy
    cleaning_log["dedup_keep"] = dedup_keep

    # PRD Expected Console Output
    print("\n" + "-"*50)
    print("CLEANING RESULTS (As per PRD Expected Outputs)")
    print("-"*50)
    print(f"Dataset Loaded Successfully")
    print(f"Rows : {original_info['rows']}")
    print(f"Columns : {original_info['columns']}")
    print(f"Missing Values Found : {total_missing}")
    print(f"Duplicate Rows Found : {dup_info['total_duplicates']}")
    print(f"Data Types Corrected : {cleaning_log.get('data_types_corrected', 0)}")
    print(f"Cleaning Completed Successfully")
    print("-"*50 + "\n")

    # Step 9: Validate Dataset
    validator = DataValidator(cleaned_df)
    validation_result = validator.validate()

    # Step 10: Generate Report
    # Step 11: Save Cleaned CSV
    exporter = DataExporter()
    saved_path = exporter.export_csv(cleaned_df, filename=output_file)
    report_path = exporter.generate_cleaning_report(
        original_info=original_info,
        cleaning_log=cleaning_log,
        final_df=cleaned_df,
        validation_result=validation_result,
        report_path=report_file
    )

    print("\n" + "#"*60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("#"*60)
    print(f"Cleaned Dataset Saved: {saved_path}")
    print(f"Cleaning Report Saved: {report_path}")
    print(f"File Name : {os.path.basename(saved_path)}")
    print("#"*60 + "\n")

    return cleaned_df


if __name__ == "__main__":
    # Default run - can be parameterized via CLI args
    import argparse

    parser = argparse.ArgumentParser(description="Data Cleaning Automation Tool")
    parser.add_argument("--input", type=str, default="data/raw_data.csv", help="Input CSV path")
    parser.add_argument("--output", type=str, default="data/cleaned_data.csv", help="Output CSV path")
    parser.add_argument("--report", type=str, default="reports/cleaning_report.txt", help="Report path")
    parser.add_argument("--missing", type=str, default="auto", 
                        choices=["auto", "mean", "median", "mode", "remove"],
                        help="Missing value strategy")
    parser.add_argument("--dedup", type=str, default="first", choices=["first", "last"], help="Dedup keep")

    args = parser.parse_args()

    # Check if file exists, if not try alternative samples
    if not os.path.exists(args.input):
        alternatives = ["data/sales.csv", "data/customers.csv", "data/employee.csv", "DataCleaningProject/data/raw_data.csv"]
        for alt in alternatives:
            if os.path.exists(alt):
                args.input = alt
                break

    run_pipeline(
        input_file=args.input,
        output_file=args.output,
        report_file=args.report,
        missing_strategy=args.missing,
        dedup_keep=args.dedup
    )
