'''
VISUALIZATION settings
Theme (light / dark / auto)

Line thickness

Show gridlines?

Enable interactive hover info

Default plot color scheme


User Preferences
Disable animations (for performance)
'''


import streamlit as st

st.title("⚙️ Settings - NOT IMPLEMENTED YET")

st.write("Configure global preferences for data processing and visualization.")

st.subheader("📊 Visualization Settings - NOT IMPLEMENTED YET")
theme = st.selectbox("Plot Theme - NOT IMPLEMENTED YET", ["Light", "Dark", "Auto"])
line_width = st.slider("Default Line Width", 1, 10, 2)
show_grid = st.checkbox("Show Gridlines", value=True)

st.subheader("👤 User Preferences")
unit_pref = st.selectbox("Voltage Units", ["mV", "V"])

# Save button - not yet implemented
if st.button("Save Settings - NOT IMPLEMENTED YET"):
    st.success("Your settings have been updated!")