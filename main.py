import streamlit as st
import pandas as pd
import numpy as np

# 1. Page Configuration
st.set_page_config(page_title="Sentinel Core", layout="wide")
st.title("Sentinel Project")
st.write("Real-time Crime Analytics Dashboard")

# 2. Optimized Data Loading
@st.cache_data
def load_data():
    # Loading 10,000 rows to prevent the "Blank Page" memory error
    file_path = 'data/raw/Crimes.csv'
    df = pd.read_csv(file_path, nrows=10000)
    
    # FIX: Standardize column names to lowercase for the map
    df.columns = [c.lower() for c in df.columns]
    
    # FIX: Rename common variations to 'latitude' and 'longitude'
    df = df.rename(columns={
        'lat': 'latitude', 
        'lon': 'longitude',
        'lat ': 'latitude',
        'long': 'longitude'
    })
    
    # FIX: Remove rows with empty location data to prevent Map Crash
    df = df.dropna(subset=['latitude', 'longitude'])
    
    return df

# Load the data
try:
    df = load_data()
    st.success("Data loaded successfully!")
    
    # 3. Sidebar Filters
    st.sidebar.header("Filter Options")
    crime_types = df['primary type'].unique() if 'primary type' in df.columns else df['category'].unique()
    selected_crime = st.sidebar.multiselect("Select Crime Type", crime_types, default=crime_types[:3])

    # Filtered Dataframe
    if 'primary type' in df.columns:
        filtered_df = df[df['primary type'].isin(selected_crime)]
    else:
        filtered_df = df

    # 4. Map Visualization
    st.subheader("Crime Hotspots Map")
    # This renders the map using the cleaned latitude/longitude
    st.map(filtered_df)

    # 5. Data Table
    if st.checkbox("Show Raw Data"):
        st.write(filtered_df.head(100))

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
    st.info("Check if 'data/raw/Crimes.csv' exists in your GitHub repo.")
