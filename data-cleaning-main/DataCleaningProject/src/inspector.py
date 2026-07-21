"""
Module 2, 3, 4, 5: Dataset Inspection, Missing Value Detection, 
Duplicate Detection, Data Type Validation
"""

import pandas as pd
import numpy as np

class DataInspector:
    """Inspect dataset structure, quality issues, and data types."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def get_basic_info(self) -> dict:
        """Returns basic dataset metrics."""
        info = {
            "rows": self.df.shape[0],
            "columns": self.df.shape[1],
            "shape": self.df.shape,
            "column_names": list(self.df.columns),
            "dtypes": self.df.dtypes.to_dict(),
            "memory_usage": self.df.memory_usage(deep=True).sum(),
            "memory_usage_mb": round(self.df.memory_usage(deep=True).sum() / (1024*1024), 2)
        }
        return info

    def display_info(self):
        """Print dataset inspection in PRD format."""
        info = self.get_basic_info()
        print("\n" + "="*50)
        print("DATASET INSPECTION")
        print("="*50)
        print(f"Rows: {info['rows']}")
        print(f"Columns: {info['columns']}")
        print(f"Shape: {info['shape']}")
        print(f"Memory: {info['memory_usage_mb']} MB")
        print(f"\nColumn Names: {', '.join(info['column_names'])}")
        print("\nData Types:")
        for col, dtype in info['dtypes'].items():
            print(f"  - {col}: {dtype}")
        print(f"\nMemory Usage (Detailed):")
        print(self.df.memory_usage(deep=True))
        print("="*50 + "\n")
        return info

    def check_missing_values(self) -> pd.DataFrame:
        """Detect null, NaN, empty cells."""
        missing_count = self.df.isnull().sum()
        # Also detect empty strings as missing
        empty_strings = self.df.apply(lambda col: col.astype(str).str.strip() == '').sum().sum()
        # Combine but avoid double counting for already null
        total_missing = missing_count.copy()
        
        missing_percent = (missing_count / len(self.df) * 100).round(2)
        
        report = pd.DataFrame({
            'Missing Values': missing_count,
            'Missing %': missing_percent,
            'Empty Strings': empty_strings
        })
        report = report[report['Missing Values'] > 0].sort_values(by='Missing Values', ascending=False)
        
        print("\n" + "="*50)
        print("MISSING VALUE DETECTION")
        print("="*50)
        if report.empty:
            print("No missing values found!")
        else:
            print(report.to_string())
            print(f"\nTotal Missing Cells: {missing_count.sum()}")
        print("="*50 + "\n")
        
        return report

    def check_duplicates(self) -> dict:
        """Detect complete duplicate rows and duplicate IDs."""
        total_dup = self.df.duplicated().sum()
        print("\n" + "="*50)
        print("DUPLICATE DETECTION")
        print("="*50)
        print(f"Complete Duplicate Rows Found: {total_dup}")

        # Check for duplicate IDs if ID-like columns exist
        id_cols = [c for c in self.df.columns if 'id' in c.lower()]
        duplicate_ids = {}
        for col in id_cols:
            dup_count = self.df.duplicated(subset=[col]).sum()
            if dup_count > 0:
                duplicate_ids[col] = dup_count
                print(f"Duplicate IDs in '{col}': {dup_count}")

        if total_dup > 0:
            print("\nSample Duplicate Rows:")
            print(self.df[self.df.duplicated(keep=False)].head(10).to_string())

        print("="*50 + "\n")
        
        return {
            "total_duplicates": total_dup,
            "duplicate_ids": duplicate_ids,
            "duplicate_rows": self.df[self.df.duplicated(keep=False)] if total_dup > 0 else pd.DataFrame()
        }

    def validate_dtypes(self) -> dict:
        """Check and suggest corrections for data types."""
        print("\n" + "="*50)
        print("DATA TYPE VALIDATION")
        print("="*50)
        
        issues = {}
        for col in self.df.columns:
            dtype = self.df[col].dtype
            sample = self.df[col].dropna().head(3).tolist()
            # Heuristic: if object but looks numeric
            if dtype == 'object':
                # Try to see if it looks like numeric
                try:
                    # Check for currency, commas
                    cleaned_sample = self.df[col].dropna().astype(str).str.replace(r'[\$,₹,]', '', regex=True).str.strip().head(10)
                    pd.to_numeric(cleaned_sample, errors='raise')
                    issues[col] = {"current": str(dtype), "suggested": "numeric (int/float)", "sample": sample}
                except:
                    # Try datetime
                    try:
                        pd.to_datetime(self.df[col].dropna().head(20), errors='raise', dayfirst=True)
                        issues[col] = {"current": str(dtype), "suggested": "datetime", "sample": sample}
                    except:
                        pass

            print(f"{col}: {dtype} | Sample: {sample[:2]}")

        if issues:
            print("\nPotential Type Issues Detected:")
            for col, info in issues.items():
                print(f"  - {col}: {info['current']} -> {info['suggested']} | Example: {info['sample'][:1]}")
        else:
            print("\nNo obvious type issues detected.")

        print("="*50 + "\n")
        return issues

    def get_summary_stats(self):
        """Display df.describe()"""
        print("\n--- Summary Statistics (Numeric) ---")
        try:
            print(self.df.describe().to_string())
        except Exception as e:
            print(f"Could not generate describe: {e}")
        print("\n--- Summary Statistics (All) ---")
        try:
            print(self.df.describe(include='all').to_string())
        except:
            pass
