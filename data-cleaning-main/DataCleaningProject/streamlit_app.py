import os
import sys
import streamlit as st
import pandas as pd
import tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.loader import DataLoader
from src.inspector import DataInspector
from src.cleaner import DataCleaner
from src.validator import DataValidator
from src.exporter import DataExporter


st.set_page_config(
    page_title="Data Cleaning Tool",
    page_icon="🧹",
    layout="wide",
)

st.title("🧹 Data Cleaning & Preprocessing Automation Tool")
st.caption("Upload a CSV, inspect quality issues, clean automatically, and download the result.")

with st.sidebar:
    st.header("⚙️ Settings")
    missing_strategy = st.selectbox(
        "Missing Value Strategy",
        ["auto", "mean", "median", "mode", "remove"],
        index=0,
    )
    dedup_keep = st.selectbox(
        "Duplicate Handling",
        ["first", "last"],
        index=0,
    )
    clean_strings = st.checkbox("Clean Strings", value=True)
    clean_numeric = st.checkbox("Clean Numeric", value=True)
    clean_dates = st.checkbox("Clean Dates", value=True)
    correct_dtypes = st.checkbox("Correct Data Types", value=True)
    preprocess = st.checkbox("Preprocess (snake_case)", value=True)

    st.divider()
    st.header("📂 Sample Datasets")
    sample_option = st.radio(
        "Choose a sample dataset",
        ["Upload your own", "raw_data.csv", "sales.csv", "customers.csv", "employee.csv"],
        index=0,
    )


def run_pipeline(df: pd.DataFrame, missing_strategy: str, dedup_keep: str,
                 clean_strings: bool, clean_numeric: bool, clean_dates: bool,
                 correct_dtypes: bool, preprocess: bool):
    inspector = DataInspector(df)
    original_info = inspector.get_basic_info()
    inspector.display_info()

    missing_report = inspector.check_missing_values()
    total_missing = df.isnull().sum().sum()
    dup_info = inspector.check_duplicates()
    dtype_issues = inspector.validate_dtypes()
    inspector.get_summary_stats()

    cleaner = DataCleaner(df)
    cleaned_df = cleaner.full_cleaning_pipeline(
        missing_strategy=missing_strategy,
        dedup_keep=dedup_keep,
        clean_strings=clean_strings,
        clean_numeric=clean_numeric,
        clean_dates=clean_dates,
        correct_dtypes=correct_dtypes,
        preprocess=preprocess,
    )

    cleaning_log = cleaner.get_cleaning_log()
    cleaning_log["missing_strategy"] = missing_strategy
    cleaning_log["dedup_keep"] = dedup_keep

    validator = DataValidator(cleaned_df)
    validation_result = validator.validate()

    exporter = DataExporter()
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = exporter.export_csv(cleaned_df, filename=os.path.join(tmpdir, "cleaned_data.csv"))
        report_path = exporter.generate_cleaning_report(
            original_info=original_info,
            cleaning_log=cleaning_log,
            final_df=cleaned_df,
            validation_result=validation_result,
            report_path=os.path.join(tmpdir, "cleaning_report.txt"),
        )
        with open(csv_path, "rb") as f:
            csv_bytes = f.read()
        with open(report_path, "r", encoding="utf-8") as f:
            report_text = f.read()

    return cleaned_df, cleaning_log, validation_result, csv_bytes, report_text


uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success(f"Loaded **{uploaded_file.name}** — {df.shape[0]} rows × {df.shape[1]} columns")
elif sample_option != "Upload your own":
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    file_path = os.path.join(data_dir, sample_option)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        st.success(f"Loaded sample **{sample_option}** — {df.shape[0]} rows × {df.shape[1]} columns")
    else:
        st.error(f"Sample file not found: {file_path}")
        st.stop()
else:
    st.info("👈 Upload a CSV file or select a sample dataset from the sidebar to get started.")
    st.stop()

if st.button("▶️ Run Cleaning Pipeline", type="primary", use_container_width=True):
    with st.spinner("Running pipeline..."):
        cleaned_df, cleaning_log, validation_result, csv_bytes, report_text = run_pipeline(
            df,
            missing_strategy=missing_strategy,
            dedup_keep=dedup_keep,
            clean_strings=clean_strings,
            clean_numeric=clean_numeric,
            clean_dates=clean_dates,
            correct_dtypes=correct_dtypes,
            preprocess=preprocess,
        )

    st.subheader("📊 Cleaning Results")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Original Rows", cleaning_log.get("original_rows", df.shape[0]))
    col2.metric("Cleaned Rows", cleaned_df.shape[0])
    col3.metric("Missing Fixed", cleaning_log.get("missing_values_fixed", 0))
    col4.metric("Duplicates Removed", cleaning_log.get("duplicates_removed", 0))

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Types Corrected", cleaning_log.get("data_types_corrected", 0))
    col6.metric("String Ops", cleaning_log.get("string_cleaning_ops", 0))
    col7.metric("Numeric Ops", cleaning_log.get("numeric_cleaning_ops", 0))
    col8.metric("Date Ops", cleaning_log.get("date_formatting_ops", 0))

    status_color = "🟢" if validation_result.get("status") == "Validation Passed" else "🔴"
    st.subheader(f"{status_color} Validation Status: {validation_result.get('status')}")

    tab1, tab2, tab3 = st.tabs(["Cleaned Data Preview", "Download CSV", "Cleaning Report"])
    with tab1:
        st.dataframe(cleaned_df.head(100), use_container_width=True)
        st.caption(f"Showing first 100 rows of {cleaned_df.shape[0]} total rows.")
    with tab2:
        st.download_button(
            label="📥 Download cleaned_data.csv",
            data=csv_bytes,
            file_name="cleaned_data.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with tab3:
        st.text_area("Report", report_text, height=500)
