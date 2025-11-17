import streamlit as st
import pandas as pd

st.title("Analyze Data Page")
st.write("Hello World! This is the Analyze Data page.")

st.write("Use the tools below to upload your data, preview it, and perform basic analysis.")

# Upload
st.markdown("### 🔼 Upload Data File")
uploaded_file = st.file_uploader("Upload CSV, Excel, or text data files", type=['csv', 'xlsx', 'txt'])

if uploaded_file:
    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

# Quick metrics
st.markdown("### ⚡ Quick Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Rows", len(df))
col2.metric("Columns", len(df.columns))
col3.metric("Missing Values", df.isna().sum().sum())