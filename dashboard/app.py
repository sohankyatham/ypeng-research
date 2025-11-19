# YPENG Data Dashboard to display key metrics 
'''
Allows researchers to upload, process, and visualize experimental data collected from piezoelctric nanogenerator experiments.

1. The user launches the app 
2. The script loads experimental data from local files
3. Data preprocessing is performed using Pandas and NumPy.
4. Processed data is displayed in various plots and summary tables.
5. Users can filter, compare, and analyze results through the dashboard interface.

RUN THIS CODE WITH:
streamlit run dashboard/app.py --server.port 8502
'''

import streamlit as st

# Set the page title and favicon
st.set_page_config(page_title="YPENG Data Dashboard", page_icon="⚡", layout="wide")

# Title
st.title("Piezoelectric Nanogenerator Data Dashboard")
st.info("Welcome to the interactive dashboard for analyzing yarn-based Piezoelectric Nanogenerator data!")


# --- Dashboard Summary Metrics - 3 Column layout for metrics ---
# Use dictionary implementation to make this more scalable to add more metrics in the future
metrics_col_datasets, metrics_col_visualizations, metrics_col_models = st.columns(3)

with metrics_col_datasets:
    st.metric("Datasets Uploaded", "0")

with metrics_col_visualizations:
    st.metric("Visualizations Created", "0")

with metrics_col_models:
    st.metric("Models Trained", "0")


# Feature Cards - three side-by-side columns
# Make the feature cards actionable links
col_upload, col_process, col_visualize = st.columns(3)

with col_upload:
    st.success("**Upload Data** \n\n Import CSV/Excel files for analysis.")

with col_process:
    st.warning("**Process Data** \n\n Clean, filter, and transform your datasets.")

with col_visualize:
    st.info("**Visualize Results** \n\n Generate voltage, current, and power plots.")


st.markdown("---")
st.markdown("ℹ️ How to use this Dashboard")
st.write("""
1. Upload your experimental data  
2. Select processing options  
3. View plots and summary tables  
4. Export/save results   
""")


# About Section 
st.markdown("## 🔬 About Our Research")
st.write("Learn more about the Innovative Materials Research Team.")

# Button to redirect users to lab website
# Add hover effect when hovering over the button
st.markdown(
"""
<a href="https://www.fcs.uga.edu/tmi/innovative-materials-research-team" target="_blank">
    <button style="font-size: 16px; border-radius: 10px; background-color: blue;">
        🌐 Visit the Website
    </button>
</a>
""",
unsafe_allow_html=True
)

# Footer 
st.markdown("---")
st.markdown("© 2025 YPENG Research | Made by Sohan Kyatham ")