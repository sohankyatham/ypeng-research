'''
Handle uploaded YPENG data

Default sampling rate

Default column names (force, voltage, displacement, etc.)

Apply smoothing by default? (checkbox)

Select smoothing algorithm (moving average, Savitzky–Golay, etc.)

Default window size for plotting




VISUALIZATION settings
Theme (light / dark / auto)

Line thickness

Show gridlines?

Enable interactive hover info

Default plot color scheme




User Preferences
Units preference (e.g., mV vs V)
Enable debugging mode

Show/hide advanced features

Disable animations (for performance)
'''


import streamlit as st

st.title("⚙️ Settings")

st.write("Configure global preferences for data processing and visualization.")

st.subheader("🔧 Data Processing")
sampling_rate = st.number_input("Default Sampling Rate (Hz)", min_value=1, value=1000)

st.subheader("📊 Visualization Settings")
theme = st.selectbox("Plot Theme", ["Light", "Dark", "Auto"])
line_width = st.slider("Default Line Width", 1, 10, 2)
show_grid = st.checkbox("Show Gridlines", value=True)

st.subheader("👤 User Preferences")
researcher_name = st.text_input("Researcher Name", "Your Name")
auto_load_last = st.checkbox("Auto-load last used dataset", value=True)
unit_pref = st.selectbox("Voltage Units", ["mV", "V"])

st.subheader("⚙️ Application Behavior")
debug_mode = st.checkbox("Enable Debug Mode")
show_advanced = st.checkbox("Show Advanced Features")

# Save button (doesn’t persist yet — you can add later with session_state / JSON)
if st.button("Save Settings"):
    st.success("Your settings have been updated!")

