# Analyze uploaded time-series data
'''
This page will allow importing CSV and Excel data for processing & analysis
'''
import streamlit as st
import pandas as pd
import altair as alt

# Set the page title and favicon
st.set_page_config(page_title="Analyze", page_icon="📊", layout="wide")

st.title("Analyze Data Page")

# --- Helpers ---
def drop_junk_columns(df_in: pd.DataFrame) -> pd.DataFrame:
    """Drop common accidental columns (like CSV-saved index columns)."""
    df_out = df_in.copy()

    # Drop columns like "Unnamed: 0" (common when saving df with index)
    junk = [c for c in df_out.columns if str(c).strip().lower().startswith("unnamed")]
    if junk:
        df_out = df_out.drop(columns=junk)

    # Drop columns that are entirely NA
    df_out = df_out.dropna(axis=1, how="all")

    return df_out

def numeric_only(df_in: pd.DataFrame) -> pd.DataFrame:
    return df_in.select_dtypes(include="number")

# Plot needs to default X to Time (s)
def best_default_x(df_in: pd.DataFrame) -> str | None:
    # Prefer exact expected column
    if "Time (s)" in df_in.columns:
        return "Time (s)"
    # Otherwise choose first numeric column if any
    num_cols = list(numeric_only(df_in).columns)
    return num_cols[0] if num_cols else None

# Plot needs to default Y to Voltage (V).
def best_default_y(df_in: pd.DataFrame, x_col: str | None) -> list[str]:
    # Prefer Voltage (V)
    if "Voltage (V)" in df_in.columns:
        return ["Voltage (V)"]
    # Otherwise pick first numeric column that isn't x
    num_cols = [c for c in numeric_only(df_in).columns if c != x_col]
    return [num_cols[0]] if num_cols else []

# ---------- Upload ----------
st.markdown("### 🔼 Upload File")
uploaded_file = st.file_uploader(
    "Upload CSV, Excel, or Text data files",
    type=["csv", "xlsx", "xlsm", "xls", "txt"],
)

# Empty DataFrame for default no file upload
df = pd.DataFrame(columns=['col1']) # Empty DataFrame

# Read Uploaded File
if uploaded_file:
    filename = uploaded_file.name
    name_only, file_extension = filename.rsplit(".", 1)
    file_extension = file_extension.lower()

    try:
        if file_extension in ["csv", "txt"]:
            # sep=None lets pandas sniff delimiters; engine="python" needed for sniffing
            df = pd.read_csv(uploaded_file, sep=None, engine="python")
        elif file_extension in ["xlsx", "xlsm", "xls"]:
            df = pd.read_excel(uploaded_file)

        df = drop_junk_columns(df)

        st.success(f"{name_only + "." + file_extension} was successfully uploaded!")
    except Exception as e:
        st.error(f"Could not read file: {e}")
        df = pd.DataFrame()
else:
    st.warning("No data file uploaded")

# ---------- Quick metrics ----------
st.markdown("### ⚡ Quick Metrics")
metrics_rows, metrics_cols, metrics_missing = st.columns(3)
metrics_rows.metric("Rows", int(len(df)))
metrics_cols.metric("Columns", int(len(df.columns)))
metrics_missing.metric("Missing Values", int(df.isna().sum().sum()) if not df.empty else 0)

# ---------- Tabs ----------
summary_tab, plot_tab, raw_table_tab = st.tabs(["📈 Summary Stats", "📉 Plot Data", "📄 Raw Table"])

with summary_tab:
    st.caption("Basic descriptive statistics for all numeric columns in the uploaded file.")
    if not df.empty:
        num_df = numeric_only(df)

        if num_df.shape[1] == 0:
            st.warning("No numeric data available to analyze.")
        else:
            describe_data = num_df.describe()

            # Peak-to-peak only for numeric columns
            describe_data.loc["peak_to_peak"] = num_df.max(numeric_only=True) - num_df.min(numeric_only=True)

            # Reorder rows (only those that exist)
            desired_order = ["min", "max", "peak_to_peak", "mean", "std", "count", "25%", "50%", "75%"]
            existing = [r for r in desired_order if r in describe_data.index]
            describe_data = describe_data.loc[existing]

            # Friendly row labels (optional)
            describe_data = describe_data.rename(index={
                "min": "Minimum",
                "max": "Maximum",
                "mean": "Mean",
                "std": "Std Dev",
                "count": "Count",
                "peak_to_peak": "Peak-to-Peak",
                "25%": "25%",
                "50%": "50%",
                "75%": "75%",
            })

            st.dataframe(describe_data, use_container_width=True)
    else:
        st.info("Upload a file to see summary statistics.")

with plot_tab:
    st.caption("Select x and y columns to visualize time-series signals such as voltage and current.")
    if df.empty:
        st.info("Upload a file to plot data.")
    else:
        # Prefer numeric columns for plotting
        num_cols = list(numeric_only(df).columns)

        if len(num_cols) == 0:
            st.warning("No numeric columns available to plot.")
        else:
            x_default = best_default_x(df)

            # X-axis selector: allow any numeric column (and also allow Time (s) if present)
            x_candidates = num_cols.copy()
            if x_default and x_default not in x_candidates:
                x_candidates.insert(0, x_default)

            x_col = st.selectbox(
                "X-axis",
                options=x_candidates,
                index=x_candidates.index(x_default) if x_default in x_candidates else 0
            )

            # Y-axis selector: numeric columns excluding x
            y_candidates = [c for c in num_cols if c != x_col]

            y_default = best_default_y(df, x_col)
            y_default = [c for c in y_default if c in y_candidates]
            if not y_default and y_candidates:
                y_default = [y_candidates[0]]

            y_cols = st.multiselect(
                "Y-axis",
                options=y_candidates,
                default=y_default
            )

            if not y_cols:
                st.warning("Pick at least one Y column to plot.")
            else:
                # Build long-form for Altair
                plot_df = df[[x_col] + y_cols].dropna()

                long_df = plot_df.melt(
                    id_vars=[x_col],
                    value_vars=y_cols,
                    var_name="Series",
                    value_name="Value",
                )

                chart = (
                    alt.Chart(long_df)
                    .mark_line()
                    .encode(
                        x=alt.X(f"{x_col}:Q", title=x_col),
                        y=alt.Y("Value:Q", title="Value"),
                        color=alt.Color("Series:N", title=""),
                        tooltip=[alt.Tooltip(f"{x_col}:Q", title=x_col),
                                 alt.Tooltip("Series:N"),
                                 alt.Tooltip("Value:Q")]
                    )
                    .properties(height=420)
                    .interactive()
                )

                st.altair_chart(chart, use_container_width=True)


with raw_table_tab:
    st.caption("View the full uploaded dataset in tabular form and download it as a CSV.")
    if df.empty:
        st.info("Upload a file to view the raw table.")
    else:
        st.dataframe(df, use_container_width=True)

        # Download EXACTLY what is displayed (no index column)
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download as CSV",
            data=csv_bytes,
            file_name="export.csv",
            mime="text/csv",
        )