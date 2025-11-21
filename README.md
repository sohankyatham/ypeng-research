# Y-PENG Research: Data Analysis & Dashboard

View the app - [https://ypeng-dashboard.streamlit.app/](https://ypeng-dashboard.streamlit.app/)

This repository contains scripts for collecting, analyzing, and visualizing data obtained through LabVIEW for the Y-PENG project, along with a deployable Streamlit dashboard to interactively explore the results.

- GUI-based CSV selection
- Error handling in GUI (not terminal) 
- Automatic visualization
- Save Analysis Results

Research scripts/workflows & data analysis jupyter notebooks in scripts/

Deployable Streamlit dashboard in dashboard/

<br><br>
**DEVELOPER NOTES FOR IMPROVEMENTS:**

General:
- Fix theme
- Fix title for each tab

app.py:
- Fix navigation to say Home, Analyze, & Settings
- For metrics - Use dictionary to make more scalable and add more metrics
- Keep track of metrics 
- Make the feature cards actionable links (i.e takes you to Analyze page when that card clicked)

analyze_data_py:
- When you exit the page and return you need to reupload the file
- Implement advanced features - normalize, remove outliers

settings_page.py:
- Implement features 
