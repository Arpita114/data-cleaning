"""
Module 1: Dataset Import
Handles CSV file import, format validation, and initial loading.
"""

import os
import pandas as pd

class DataLoader:
    """Responsible for loading and validating CSV datasets."""
    
    SUPPORTED_FORMATS = ['.csv']

    @staticmethod
    def validate_file(file_path: str) -> bool:
        """Validate file existence and format."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in DataLoader.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {ext}. Supported: {DataLoader.SUPPORTED_FORMATS}")
        
        if os.path.getsize(file_path) == 0:
            raise ValueError(f"File is empty: {file_path}")
        
        return True

    @staticmethod
    def load_csv(file_path: str, **kwargs) -> pd.DataFrame:
        """
        Load CSV file using Pandas with error handling.
        
        Args:
            file_path: Path to CSV file
            **kwargs: Additional args for pd.read_csv
            
        Returns:
            pd.DataFrame: Loaded dataset
        """
        try:
            DataLoader.validate_file(file_path)
            # Try to handle common issues automatically
            df = pd.read_csv(file_path, **kwargs)
            print(f"[Loader] Dataset successfully loaded from: {file_path}")
            return df
        except Exception as e:
            print(f"[Loader] ERROR loading dataset: {e}")
            raise

    @staticmethod
    def load_sample_datasets(data_dir: str = "data/"):
        """Load predefined sample files if they exist."""
        sample_files = ["sales.csv", "customers.csv", "employee.csv", "raw_data.csv"]
        datasets = {}
        for fname in sample_files:
            fpath = os.path.join(data_dir, fname)
            if os.path.exists(fpath):
                try:
                    datasets[fname] = DataLoader.load_csv(fpath)
                except Exception as e:
                    print(f"[Loader] Skipping {fname}: {e}")
        return datasets
