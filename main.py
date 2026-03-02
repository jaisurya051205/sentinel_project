import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Setup Command Center Layout
st.set_page_config(page_title="Sentinel Command Center", layout="wide")
st.title("🚨 Sentinel Core: Command Center")

# 2. Load Data with a higher row count for "Fuller" map
@st.cache_data
def load_data():
    # 25,000 rows is the "sweet spot" for performance
    df = pd.read_csv('data/raw/Crimes.csv', nrows=25000)
    df.columns = [c.lower().strip() for c in df.columns]
    df = df.rename(columns={'lat': 'latitude', 'lon': 'longitude'})
    df = df.dropna(subset=['latitude', 'longitude'])
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df

try:
    df = load_data()

    # 3. Top Row: Command Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Patrols", len(df))
    col2.metric("Districts Covered", df['district'].nunique() if 'district' in df.columns else "N/A")
    col3.metric("System Status", "ONLINE", delta="Stable")

    # 4. Sidebar: Control Panel
    st.sidebar.header("🕹️ Control Panel")
    crime_types = df['primary type'].unique().tolist()
    selected = st.sidebar.multiselect("Filter Crime Types", crime_types, default=crime_types[:3])
    
    filtered_df = df[df['primary type'].isin(selected)]

    # 5. The Patrol Map
    st.subheader("📍 Live Patrol Map")
    st.map(filtered_df, color="#FF0000")

    # 6. Command Charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("📊 Crime Breakdown")
        fig = px.pie(filtered_df, names='primary type', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        st.subheader("📈 Patrol Trends")
        if 'date' in filtered_df.columns:
            trend = filtered_df.resample('D', on='date').size().reset_index(name='count')
            st.line_chart(trend.set_index('date'))

except Exception as e:
    st.error(f"Command Center Error: {e}")
