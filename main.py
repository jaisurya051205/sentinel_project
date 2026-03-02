import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Command Center Configuration
st.set_page_config(page_title="Sentinel Command Center", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a "Dark Mode" Command Center look
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚨 Sentinel Core: Command Center")
st.markdown("---")

# 2. Data Loading Engine
@st.cache_data
def load_full_center_data():
    file_path = 'data/raw/Crimes.csv'
    # Increased to 25,000 rows for a "fuller" patrol map
    df = pd.read_csv(file_path, nrows=25000)
    df.columns = [str(c).lower().strip() for c in df.columns]
    
    # Cleaning for mapping
    df = df.rename(columns={'lat': 'latitude', 'lon': 'longitude', 'long': 'longitude'})
    df = df.dropna(subset=['latitude', 'longitude'])
    
    # Ensure Date is usable
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df

try:
    df = load_full_center_data()
    
    # 3. Top-Level Command Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Patrols", f"{len(df):,}")
    
    # Calculate Arrest Rate if column exists
    if 'arrest' in df.columns:
        arrest_rate = (df['arrest'].sum() / len(df)) * 100
        col2.metric("Arrest Rate", f"{arrest_rate:.1f}%")
    else:
        col2.metric("System Status", "Active")
        
    col3.metric("Districts Active", df['district'].nunique() if 'district' in df.columns else "N/A")
    col4.metric("Risk Level", "Elevated", delta="-2%", delta_color="inverse")

    # 4. Sidebar Control Panel
    st.sidebar.title("🎮 Control Panel")
    column_to_filter = 'primary type' if 'primary type' in df.columns else df.columns[1]
    crime_list = df[column_to_filter].unique().tolist()
    selected_crimes = st.sidebar.multiselect("Filter Patrol Types", crime_list, default=crime_list[:5])
    
    # Filter the data
    filtered_df = df[df[column_to_filter].isin(selected_crimes)]

    # 5. Main Dashboard Layout
    left_chart, right_map = st.columns([1, 2])

    with left_chart:
        st.subheader("📊 Crime Distribution")
        fig_bar = px.bar(filtered_df[column_to_filter].value_counts().head(10), 
                         orientation='h', color_discrete_sequence=['#ff4b4b'])
        fig_bar.update_layout(showlegend=False, height=400, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.subheader("📈 Temporal Trend")
        trend_data = filtered_df.resample('D', on='date').size().reset_index(name='count')
        st.line_chart(trend_data.set_index('date'))

    with right_map:
        st.subheader("📍 Live Patrol Map")
        # Use st.map for a clean, interactive patrol view
        st.map(filtered_df, color="#ff4b4b", size=20)

    # 6. Detailed Intel Logs
    with st.expander("📝 View Detailed Intel Logs"):
        st.dataframe(filtered_df.head(100), use_container_width=True)

except Exception as e:
    st.error(f"Command Center Offline: {e}")
