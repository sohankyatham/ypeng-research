# Homepage for YPENG Data Dashboard  
'''
Allows researchers to upload, process, and visualize experimental data collected from piezoelctric nanogenerator experiments.

1. The user launches the app 
2. The script loads experimental data from local files
3. Data preprocessing is performed using Pandas and NumPy.
4. Processed data is displayed in various plots and summary tables.
5. Users can filter, compare, and analyze results through the dashboard interface.
'''

import streamlit as st

# Set the page title and favicon
st.set_page_config(page_title="YPENG Data Dashboard", page_icon="⚡", layout="wide")

# Title
st.title("Piezoelectric Nanogenerator Data Dashboard")
st.info("Welcome to the Y-PENG Data Dashboard! Upload experimental data to automatically compute key performance metrics and generate publication-ready plots.")


# --- Feature Cards - three side-by-side columns ---
col_upload, col_process, col_visualize = st.columns(3)

with col_upload:
    st.success("**Upload Data** \n\n Import CSV, text, and Excel files containing time‑series data for analysis")

with col_process:
    st.success("**Process Data** \n\n Inspect time-series data, remove bad rows, and prepare datasets for plotting.")

with col_visualize:
    st.success("**Visualize & Export Results** \n\n Generate voltage, current, and power plots for Y-PENG devices.")


# -- Get Started -- 
st.subheader("Get started")

# Analyze Data Page - Actionable Link
st.page_link("pages/Analyze.py", label="Go to Analyze Data ->", icon="📊")

# Quick Guide
with st.expander("Quick Guide", expanded=True):
    st.write("1. Upload: Load your PENG dataset (time, voltage, current, etc.) via the Analyze Data page.")
    st.write("2. Explore: Check row/column counts, missing values, and summary statistics.")
    st.write("3. Visualize & export: Generate plots or view the raw table, then export results.")


# --- About Section ---
st.markdown("## 🔬 About Our Research")
st.write("Learn more about the Innovative Materials Research Team.")

# --- Button to redirect users to lab website ---
# Custom CSS for hover effect
st.markdown("""
<style>
.visit-website-btn {
    text-decoration: none !important; 
    color: white !important;
    background-color: #1b6934 !important;
    font-size: 16px;
    padding: 10px 18px;
    border-radius: 10px;
    transition: 0.6s;
}

/* Hover Effect */
.visit-website-btn:hover {
    text-decoration: underline !important;
    color: white !important;
    background-color: #238c45 !important;
    font-size: 16.5px;
    padding: 10.5px 18.5px;
}
</style>
""", unsafe_allow_html=True)

# Button - Redirects users to lab website
st.markdown(
    """
    <a href="https://www.fcs.uga.edu/tmi/innovative-materials-research-team" 
       target="_blank" 
       class="visit-website-btn">
        🌐 Visit the Website
    </a>
    """,
    unsafe_allow_html=True
)

# Footer 
st.markdown("---")
st.markdown("© Innovative Materials Team at The University of Georgia")