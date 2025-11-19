'''
This page will allow importing CSV and Excel data for processing & analysis
'''

import streamlit as st
import pandas as pd

st.title("Analyze Data Page")

# Upload File
st.markdown("### 🔼 Upload File")
uploaded_file = st.file_uploader("Upload CSV, Excel, or Text data files", type=['csv', 'xlsx', 'xlsm', 'xls', 'txt'])

# Empty DataFrame for default no file upload
df = pd.DataFrame(columns=['col1']) # Empty DataFrame

# Read Uploaded File
if uploaded_file:
    st.balloons() 
    filename = uploaded_file.name
    # Split filename and extension
    # Normalize filename extension in case user uploads file with incorrect case for extension (i.e data.CsV)
    filename, file_extension = filename.rsplit(".", 1)
    file_extension = file_extension.lower()

    # Read .csv or .txt file
    if file_extension in ["csv", "txt"]:
        df = pd.read_csv(uploaded_file, sep=None, engine="python")  
        st.success(f"{filename} was successfully uploaded!")
    # Read a variety of Excel file types
    elif file_extension in ["xlsx", "xlsm", "xls"]:
        df = pd.read_excel(uploaded_file)
        st.success(f"{filename} was successfully uploaded!") 
else:
    st.warning("No data file uploaded")

# Quick metrics
if uploaded_file:
    st.markdown("### ⚡ Quick Metrics")
    metrics_rows, metrics_cols, metrics_missing = st.columns(3)
    metrics_rows.metric("Rows", len(df))
    metrics_cols.metric("Columns", len(df.columns))
    metrics_missing.metric("Missing Values", df.isna().sum().sum())
# If no file uploaded, then metrics should be 0
else:
    st.markdown("### ⚡ Quick Metrics")
    metrics_rows, metrics_cols, metrics_missing = st.columns(3)
    metrics_rows.metric("Rows", len(df))
    metrics_cols.metric("Columns", len(df.columns) - 1)
    metrics_missing.metric("Missing Values", df.isna().sum().sum())

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Summary Stats", "📉 Plot Data", "📄 Raw Table"])
    
with tab1:
    st.write(df.describe())

with tab2:
    st.line_chart(df)

with tab3:
    st.dataframe(df)

# Advanced options
with st.expander("Advanced Options - features not implemented yet"):
    normalize = st.checkbox("Normalize data")
    remove_outliers = st.checkbox("Remove outliers")