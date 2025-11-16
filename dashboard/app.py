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
# Favicon
st.set_page_config(page_title="YPENG Data Dashboard", page_icon="⚡", layout="wide")

# Title
st.title("Piezoelectric Nanogenerator Data Dashboard")
st.write("Welcome to the interactive dashboard for analyzing yarn-based Piezoelectric Nanogenerator data!")

# Metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Samples Processed", "0")

with col2:
    st.metric("Datasets Uploaded", "0")

with col3:
    st.metric("Visualizations Created", "0")



# Simple label or text
st.info("This dashboard will soon include plots, data uploads, and analytics.")



# Navigation

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Home", "Analyze Data", "Visualization", "Other tools will be added soon"])

st.sidebar.markdown("## ⚙️ Dashboard Controls")
st.sidebar.info("Use the navigation tabs to explore features.")

st.sidebar.markdown("### 🧪 About")
st.sidebar.write("Research dashboard for YPENG experiments.")

# Theme
#theme = st.sidebar.selectbox("Theme Mode (Mock)", ["Light", "Dark"])
st.sidebar.markdown("Made by: **Sohan Kyatham**")


# Cards
colA, colB, colC = st.columns(3)

with colA:
    st.success("**Upload Data**\n\nImport CSV/Excel files for analysis.")

with colB:
    st.warning("**Process Data**\n\nClean, filter, and transform your datasets.")

with colC:
    st.info("**Visualize Results**\n\nGenerate voltage, current, and power plots.")


with st.expander("📁 Upcoming: Data Upload"):
    st.write("This section will allow importing CSV, Excel, and live sensor data.")

with st.expander("📊 Upcoming: Automatic Visualization"):
    st.write("Plot voltage, current, power output, and strain vs time.")




with st.expander("ℹ️ How this Dashboard Works"):
    st.write("""
    1. Upload your experimental data  
    2. Select processing options  
    3. View plots and summary tables  
    4. Export results for publication  
    """)


st.subheader("Quick Actions")

col_q1, col_q2, col_q3 = st.columns(3)

with col_q1:
    st.button("Upload Dataset")

with col_q2:
    st.button("View Recent Files")

with col_q3:
    st.button("Generate Report")


# Footer 
st.markdown("---")
st.markdown("© 2025 YPENG Research | Made by Sohan Kyatham | Powered by Streamlit")