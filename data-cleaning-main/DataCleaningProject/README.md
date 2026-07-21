# Data Cleaning & Preprocessing Automation Tool

A Python-based automation tool built with **Streamlit**, **Pandas**, and **NumPy** that imports raw datasets, identifies quality issues, cleans data using configurable techniques, and exports a cleaned dataset ready for analysis or machine learning.

## 🚀 Live Demo

**Deployed on Streamlit Community Cloud**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://data-cleaning-tool.streamlit.app)

> Replace the link above with your deployed app URL after pushing to GitHub and deploying on [share.streamlit.io](https://share.streamlit.io).

## 🎯 Objectives

- Automate initial stages of data analysis
- Reduce manual cleaning effort
- Improve data quality & reproducibility
- Provide an interactive web UI for non-technical users

## ✨ Features

| Module | Capability |
|--------|-----------|
| **Dataset Import** | CSV import via Pandas with format validation |
| **Dataset Inspection** | Rows, Columns, Shape, Memory usage, Data types |
| **Missing Value Detection** | Null, NaN, Empty cells with column-wise % report |
| **Duplicate Detection** | Complete duplicate rows and duplicate IDs |
| **Data Type Validation** | Suggests corrections (Object → Int/Float/Date) |
| **Data Cleaning** | Missing values (remove/mean/median/mode/auto), Duplicates, String cleaning, Date formatting, Numeric cleaning |
| **Preprocessing** | Rename to snake_case, Drop unwanted columns |
| **Validation** | Post-cleaning checks with pass/fail status |
| **Export** | CSV export of cleaned dataset |
| **Report** | Comprehensive cleaning report generated automatically |

## 📁 Project Structure

```
DataCleaningProject/
├── src/
│   ├── loader.py          # CSV loading & validation
│   ├── inspector.py       # Dataset inspection & diagnostics
│   ├── cleaner.py         # Core cleaning engine
│   ├── validator.py       # Post-cleaning validation
│   └── exporter.py        # CSV export & report generation
├── data/
│   ├── raw_data.csv       # Sample dataset
│   ├── sales.csv          # Sample dataset
│   ├── customers.csv      # Sample dataset
│   ├── employee.csv       # Sample dataset
│   └── cleaned_*.csv      # Output files (generated)
├── reports/
│   └── *_cleaning_report.txt  # Generated reports
├── streamlit_app.py       # Streamlit Community Cloud entry point
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml        # Streamlit theme config
├── main.py                # CLI entry point
├── README.md
└── LICENSE
```

## 🔧 Installation

```bash
git clone https://github.com/<your-username>/DataCleaningProject.git
cd DataCleaningProject
pip install -r requirements.txt
```

## 🚀 Usage

### Option 1: Web App (Streamlit)

```bash
streamlit run streamlit_app.py
```

### Option 2: Command Line

```bash
# Basic run
python main.py

# With options
python main.py --input data/sales.csv --output data/cleaned_data.csv --missing mean --dedup first

# As a module
python main.py --input data/raw_data.csv --missing auto --dedup first
```

### Option 3: Python Module

```python
from src.loader import DataLoader
from src.inspector import DataInspector
from src.cleaner import DataCleaner
from src.validator import DataValidator
from src.exporter import DataExporter

df = DataLoader.load_csv("data/raw_data.csv")
inspector = DataInspector(df)
inspector.display_info()

cleaner = DataCleaner(df)
cleaned_df = cleaner.full_cleaning_pipeline(missing_strategy="auto")

validator = DataValidator(cleaned_df)
validator.validate()

exporter = DataExporter()
exporter.export_csv(cleaned_df, filename="data/cleaned_data.csv")
exporter.generate_cleaning_report(...)
```

## 📊 Sample Output

```
Dataset Loaded Successfully
Rows : 50
Columns : 10
Missing Values Found : 7
Duplicate Rows Found : 0
Data Types Corrected : 1
Cleaning Completed Successfully
Cleaned Dataset Saved: data/cleaned_data.csv
Validation Passed
```

## ☁️ Deploying to Streamlit Community Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"** and select your repository
4. Set the **main file path** to `streamlit_app.py`
5. Click **Deploy**

The app will be live at `https://<your-app-name>.streamlit.app`.

## 📈 Performance

- 500 MB max dataset
- <10 sec for small datasets (<50k rows)

## 📝 Sample Datasets

| File | Rows | Columns | Description |
|------|------|---------|-------------|
| `raw_data.csv` | 50 | 10 | Employee data with missing values, duplicates, mixed dates, currency symbols |
| `sales.csv` | 15 | 8 | Sales orders with duplicate IDs and currency-formatted prices |
| `customers.csv` | 11 | 8 | Customer records with missing phone numbers and emails |
| `employee.csv` | 13 | 7 | Employee roster with manager relationships and join dates |

## 📋 Dependencies

```
streamlit>=1.30.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
openpyxl>=3.1.0
```

## 📄 License

MIT License

---

**Author:** Data Cleaning Automation v1.0
