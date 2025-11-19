# Y-PENG Research: Data Analysis & Dashboard

This repository contains scripts for collecting, analyzing, and visualizing data obtained through LabVIEW for the Y-PENG project, along with a deployable Streamlit dashboard to interactively explore the results.

- GUI-based CSV selection
- Error handling in GUI (not terminal) 
- Automatic visualization
- Save Analysis Results

Research scripts/workflows & data analysis jupyter notebooks in scripts/

Deployable Streamlit dashboard in dashboard/


Developer Notes for Improvements:

app.py:
- Fix navigation to say Home, Analyze, & Settings
- For metrics - Use dictionary to make more scalable and add more metrics
- Make the feature cards actionable links (i.e takes you to Analyze page when that card clicked)
- About Section: Make button have a hover effect 