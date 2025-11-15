# Dashboard (deployable Streamlit app) to display key metrics 
'''
Allows researchers to upload, process, and visualize experimental data collected from piezoelctric nanogenerator experiments.

1. The user launches the app via Streamlit (e.g., `streamlit run app.py`).
2. The script loads experimental data from local files or external sources.
3. Data preprocessing is performed using Pandas and NumPy.
4. Processed data is displayed in various plots and summary tables.
5. Users can filter, compare, and analyze results through the dashboard interface.

This file manages UI layout, data handling, and visualization logic to deliver 
a complete, interactive analytical tool for research and presentation.

RUN THIS CODE WITH:
streamlit run dashboard/app.py --server.port 8502
'''

import streamlit as st

# Set the page title and layout
st.set_page_config(page_title="YPENG Data Dashboard", layout="wide")

# Title
st.title("Piezoelectric Nanogenerator Data Dashboard")

st.markdown("""
Yarn-Based Piezoelectric Nanogenerator (YPENG) Dashboard  
Easily upload, explore, and visualize your experimental data.
""")

# Simple label or text
st.write("Welcome to the interactive dashboard for analyzing yarn-based Piezoelectric Nanogenerator data!")
st.info("This dashboard will soon include plots, data uploads, and analytics.")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Home", "Analyze Data", "Visualization", "Other tools will be added soon"])