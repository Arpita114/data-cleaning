"""
Module 8: Data Validation
Check missing values after cleaning, duplicate records after cleaning, invalid data types.
"""

import pandas as pd

class DataValidator:
    """Validates cleaned dataset."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def validate(self) -> dict:
        """Run all validation checks."""
        results = {}

        # Missing values
        missing = self.df.isnull().sum().sum()
        results["remaining_nulls"] = int(missing)
        results["missing_by_column"] = self.df.isnull().sum().to_dict()

        # Duplicates
        dup_count = self.df.duplicated().sum()
        results["remaining_duplicates"] = int(dup_count)

        # Invalid data types - check for object columns that still contain mixed types or suspicious values
        invalid_types = {}
        for col in self.df.columns:
            # If column is supposed to be numeric but has non-numeric strings (should be already cleaned)
            if pd.api.types.is_object_dtype(self.df[col]):
                # Check if still contains special characters like $, etc that should have been cleaned
                sample_str = self.df[col].dropna().astype(str)
                if sample_str.str.contains(r'[\$,₹]').any():
                    invalid_types[col] = "Contains currency symbols"
                # Check for leading/trailing spaces
                if sample_str.str.contains(r'^\s+|\s+$', regex=True).any():
                    invalid_types[col] = "Contains extra spaces"

        results["invalid_types"] = invalid_types

        # Overall validation status
        if missing == 0 and dup_count == 0 and not invalid_types:
            results["status"] = "Validation Passed"
        else:
            results["status"] = "Validation Issues Found"

        # Print report
        print("\n" + "="*50)
        print("DATA VALIDATION")
        print("="*50)
        print(f"Remaining Null Values: {missing}")
        print(f"Remaining Duplicate Rows: {dup_count}")
        if invalid_types:
            print("Invalid Data Type Issues:")
            for col, issue in invalid_types.items():
                print(f"  - {col}: {issue}")
        else:
            print("Invalid Type Checks: No issues")
        
        print(f"\nStatus: {results['status']}")
        print("="*50 + "\n")

        return results

    def generate_validation_summary(self) -> str:
        """Return human readable summary."""
        res = self.validate()
        summary = f"""
Validation Summary:
- Remaining Nulls: {res['remaining_nulls']}
- Remaining Duplicates: {res['remaining_duplicates']}
- Invalid Type Issues: {len(res['invalid_types'])}
- Status: {res['status']}
"""
        return summary
