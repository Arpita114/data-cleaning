"""
Module 6 & 7: Data Cleaning & Data Preprocessing
Implements all cleaning operations from PRD.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Union

class DataCleaner:
    """Core cleaning engine handling missing values, duplicates, strings, dates, numeric."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.original_shape = df.shape
        self.cleaning_log = {
            "missing_values_fixed": 0,
            "duplicates_removed": 0,
            "data_types_corrected": 0,
            "string_cleaning_ops": 0,
            "numeric_cleaning_ops": 0,
            "date_formatting_ops": 0
        }

    # -------------------- Missing Values --------------------
    def clean_missing_values(self, strategy: str = "auto", custom_map: Dict = None, columns: List[str] = None) -> pd.DataFrame:
        """
        Clean missing values with multiple options.
        strategy: 'remove', 'mean', 'median', 'mode', 'custom', 'auto'
        auto: numeric->mean, categorical->mode
        """
        target_cols = columns if columns else self.df.columns.tolist()
        before_missing = self.df.isnull().sum().sum()

        for col in target_cols:
            if self.df[col].isnull().sum() == 0:
                continue

            if strategy == "remove":
                self.df = self.df.dropna(subset=[col]).copy()

            elif strategy == "mean":
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    self.df[col] = self.df[col].fillna(self.df[col].mean())
                else:
                    try:
                        numeric = pd.to_numeric(self.df[col].astype(str).str.replace(r'[,₹$]', '', regex=True), errors='coerce')
                        if numeric.notna().sum() / len(self.df) > 0.5:
                            self.df[col] = numeric
                            self.df[col] = self.df[col].fillna(self.df[col].mean())
                        else:
                            mode_val = self.df[col].mode()
                            fill_val = mode_val[0] if not mode_val.empty else "Unknown"
                            self.df[col] = self.df[col].fillna(fill_val)
                    except:
                        mode_val = self.df[col].mode()
                        fill_val = mode_val[0] if not mode_val.empty else "Unknown"
                        self.df[col] = self.df[col].fillna(fill_val)

            elif strategy == "median":
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    self.df[col] = self.df[col].fillna(self.df[col].median())
                else:
                    try:
                        numeric = pd.to_numeric(self.df[col].astype(str).str.replace(r'[,₹$]', '', regex=True), errors='coerce')
                        if numeric.notna().sum() / len(self.df) > 0.5:
                            self.df[col] = numeric
                            self.df[col] = self.df[col].fillna(self.df[col].median())
                        else:
                            mode_val = self.df[col].mode()
                            fill_val = mode_val[0] if not mode_val.empty else "Unknown"
                            self.df[col] = self.df[col].fillna(fill_val)
                    except:
                        mode_val = self.df[col].mode()
                        fill_val = mode_val[0] if not mode_val.empty else "Unknown"
                        self.df[col] = self.df[col].fillna(fill_val)

            elif strategy == "mode":
                mode_val = self.df[col].mode()
                fill_val = mode_val[0] if not mode_val.empty else "Unknown"
                self.df[col] = self.df[col].fillna(fill_val)

            elif strategy == "custom":
                if custom_map and col in custom_map:
                    self.df[col] = self.df[col].fillna(custom_map[col])

            elif strategy == "auto":
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    self.df[col] = self.df[col].fillna(self.df[col].mean())
                else:
                    temp = pd.to_numeric(self.df[col].astype(str).str.replace(r'[,₹$]', '', regex=True), errors='coerce')
                    if temp.notna().sum() / len(self.df) > 0.5:
                        self.df[col] = temp
                        self.df[col] = self.df[col].fillna(self.df[col].mean())
                    else:
                        mode_val = self.df[col].mode()
                        fill_val = mode_val[0] if not mode_val.empty else "Unknown"
                        self.df[col] = self.df[col].fillna(fill_val)

        after_missing = self.df.isnull().sum().sum()
        self.cleaning_log["missing_values_fixed"] = int(before_missing - after_missing)
        print(f"[Cleaner] Missing Values Fixed: {self.cleaning_log['missing_values_fixed']} (Strategy: {strategy})")
        return self.df

    def remove_rows_with_missing(self, thresh: float = None):
        """Remove rows with missing - alternative API."""
        before = len(self.df)
        if thresh:
            self.df = self.df.dropna(thresh=int(thresh * len(self.df.columns))).copy()
        else:
            self.df = self.df.dropna().copy()
        removed = before - len(self.df)
        print(f"[Cleaner] Removed {removed} rows containing missing values")
        return self.df

    # -------------------- Duplicates --------------------
    def remove_duplicates(self, keep: str = "first", subset: List[str] = None) -> pd.DataFrame:
        """
        Remove duplicate records.
        keep: 'first', 'last', False
        """
        before = len(self.df)
        self.df = self.df.drop_duplicates(keep=keep, subset=subset).copy()
        after = len(self.df)
        removed = before - after
        self.cleaning_log["duplicates_removed"] = removed
        print(f"[Cleaner] Duplicate Records Removed: {removed} (keep={keep})")
        return self.df

    # -------------------- String Cleaning --------------------
    def clean_strings(self, lowercase: bool = False, uppercase: bool = False, 
                      trim_spaces: bool = True, remove_special: bool = False,
                      columns: List[str] = None) -> pd.DataFrame:
        """String cleaning per PRD."""
        str_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        target_cols = columns if columns else str_cols

        ops = 0
        for col in target_cols:
            if col not in self.df.columns:
                continue
            if not pd.api.types.is_object_dtype(self.df[col]) and not pd.api.types.is_string_dtype(self.df[col]):
                continue

            if trim_spaces:
                self.df[col] = self.df[col].astype(str).str.strip()
                self.df[col] = self.df[col].str.replace(r'\s+', ' ', regex=True)
                self.df[col] = self.df[col].replace({'nan': np.nan, 'None': np.nan, 'NULL': np.nan, 'null': np.nan})
                ops += 1

            if lowercase:
                self.df[col] = self.df[col].str.lower()
                ops += 1
            elif uppercase:
                self.df[col] = self.df[col].str.upper()
                ops += 1

            if remove_special:
                self.df[col] = self.df[col].astype(str).str.replace(r'[^\w\s@.\-]', '', regex=True)
                ops += 1

        self.cleaning_log["string_cleaning_ops"] = ops
        print(f"[Cleaner] String Cleaning Operations Applied: {ops}")
        return self.df

    # -------------------- Date Formatting --------------------
    def clean_dates(self, columns: List[str] = None, target_format: str = "%Y-%m-%d") -> pd.DataFrame:
        """Convert mixed date formats to uniform YYYY-MM-DD."""
        if columns is None:
            potential_date_cols = [c for c in self.df.columns if 'date' in c.lower() or 'time' in c.lower()]
            for col in self.df.select_dtypes(include=['object']).columns:
                if col in potential_date_cols:
                    continue
                sample = self.df[col].dropna().astype(str).head(20)
                if len(sample) == 0:
                    continue
                date_like = sample.str.contains(r'\d{1,4}[-/]\d{1,2}[-/]\d{1,4}', regex=True, na=False).mean()
                if date_like > 0.5:
                    potential_date_cols.append(col)
            columns = potential_date_cols

        fixed = 0
        for col in columns:
            if col not in self.df.columns:
                continue
            try:
                original = self.df[col].copy()
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce', dayfirst=True)
                converted = self.df[col].notna().sum() - original.isna().sum()
                if converted > 0 or self.df[col].notna().sum() > 0:
                    self.df[col] = self.df[col].dt.strftime(target_format)
                    self.df[col] = self.df[col].replace({'NaT': np.nan})
                    fixed += 1
            except Exception as e:
                print(f"[Cleaner] Could not parse date column {col}: {e}")

        self.cleaning_log["date_formatting_ops"] = fixed
        print(f"[Cleaner] Date Columns Formatted: {fixed} -> Target: {target_format} (YYYY-MM-DD)")
        return self.df

    # -------------------- Numeric Cleaning --------------------
    def clean_numeric(self, columns: List[str] = None) -> pd.DataFrame:
        """Remove commas, currency symbols, handle negative values."""
        if columns is None:
            columns = self.df.select_dtypes(include=['object']).columns.tolist()

        cleaned = 0
        for col in columns:
            if col not in self.df.columns:
                continue
            if not pd.api.types.is_object_dtype(self.df[col]) and not pd.api.types.is_string_dtype(self.df[col]):
                continue
            if len(self.df[col].dropna()) == 0:
                continue

            sample_has_numeric = self.df[col].dropna().astype(str).head(20).str.contains(r'[\$,₹,]').any()
            if not sample_has_numeric:
                continue

            original = self.df[col].copy()
            self.df[col] = self.df[col].astype(str).str.replace(r'[\$,₹€£¥]', '', regex=True)
            self.df[col] = self.df[col].str.replace(',', '', regex=False)
            self.df[col] = self.df[col].str.strip()
            self.df[col] = self.df[col].str.replace(r'^\((.*)\)$', r'-\1', regex=True)
            converted = pd.to_numeric(self.df[col], errors='coerce')
            if converted.notna().sum() / len(self.df) > 0.5:
                self.df[col] = converted
                cleaned += 1
            else:
                if original.astype(str).str.contains(r'^\d').mean() < 0.3:
                    self.df[col] = original

        self.cleaning_log["numeric_cleaning_ops"] = cleaned
        print(f"[Cleaner] Numeric Columns Cleaned: {cleaned} (removed commas, currency)")
        return self.df

    # -------------------- Data Type Correction --------------------
    def correct_dtypes(self) -> pd.DataFrame:
        """Attempt to correct data types: object -> int/float/datetime where appropriate."""
        corrected = 0
        for col in self.df.columns:
            original_dtype = self.df[col].dtype
            
            if pd.api.types.is_numeric_dtype(original_dtype) or pd.api.types.is_datetime64_any_dtype(original_dtype):
                continue

            cleaned_str = self.df[col].astype(str).str.replace(r'[\$,₹,]', '', regex=True).str.strip()
            numeric_attempt = pd.to_numeric(cleaned_str, errors='coerce')
            if len(self.df[col].dropna()) > 0 and numeric_attempt.notna().sum() / len(self.df[col].dropna()) > 0.8:
                if (numeric_attempt.dropna() % 1 == 0).all():
                    self.df[col] = numeric_attempt.astype('Int64')
                else:
                    self.df[col] = numeric_attempt.astype(float)
                corrected += 1
                continue

            try:
                datetime_attempt = pd.to_datetime(self.df[col], errors='coerce', dayfirst=True)
                if len(self.df[col].dropna()) > 0 and datetime_attempt.notna().sum() / len(self.df[col].dropna()) > 0.6:
                    self.df[col] = datetime_attempt
                    corrected += 1
            except:
                pass

            lower_vals = self.df[col].dropna().astype(str).str.lower().unique()
            bool_vals = {'true', 'false', '1', '0', 'yes', 'no', 't', 'f', 'y', 'n'}
            if set(lower_vals).issubset(bool_vals) and len(lower_vals) <= 4:
                mapping = {'true': True, 'false': False, '1': True, '0': False, 'yes': True, 'no': False, 't': True, 'f': False, 'y': True, 'n': False}
                self.df[col] = self.df[col].astype(str).str.lower().map(mapping)
                corrected += 1

        self.cleaning_log["data_types_corrected"] = corrected
        print(f"[Cleaner] Data Types Corrected: {corrected}")
        return self.df

    # -------------------- Preprocessing --------------------
    def preprocess(self, rename_map: Dict = None, drop_cols: List[str] = None, 
                   lowercase_cols: bool = True, create_new_cols: bool = False) -> pd.DataFrame:
        """Module 7: Preprocessing Tasks."""
        if lowercase_cols:
            new_names = {}
            for col in self.df.columns:
                clean_name = col.strip().lower()
                clean_name = re.sub(r'\s+', '_', clean_name)
                clean_name = re.sub(r'[^\w_]', '', clean_name)
                new_names[col] = clean_name
            self.df = self.df.rename(columns=new_names)
            print(f"[Preprocess] Columns renamed to snake_case: {list(new_names.values())}")

        if rename_map:
            self.df = self.df.rename(columns=rename_map)

        if drop_cols:
            existing = [c for c in drop_cols if c in self.df.columns]
            if existing:
                self.df = self.df.drop(columns=existing)
                print(f"[Preprocess] Dropped columns: {existing}")

        return self.df

    def full_cleaning_pipeline(self, missing_strategy="auto", dedup_keep="first",
                               clean_strings=True, clean_numeric=True, clean_dates=True,
                               correct_dtypes=True, preprocess=True) -> pd.DataFrame:
        """Run complete pipeline in order defined by PRD."""
        print("\n" + "="*50)
        print("STARTING FULL CLEANING PIPELINE")
        print("="*50)
        
        if clean_numeric:
            self.clean_numeric()
        if correct_dtypes:
            self.correct_dtypes()
        if clean_strings:
            self.clean_strings(trim_spaces=True, lowercase=False, uppercase=False, remove_special=False)
        if clean_dates:
            self.clean_dates()
        self.clean_missing_values(strategy=missing_strategy)
        self.remove_duplicates(keep=dedup_keep)
        if preprocess:
            self.preprocess(lowercase_cols=True)

        print("="*50)
        print("CLEANING PIPELINE COMPLETED")
        print("="*50 + "\n")
        return self.df

    def get_cleaning_log(self):
        return self.cleaning_log
