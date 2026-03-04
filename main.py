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
    file_path = 'data/raw/Crimes.csv'
    # Loading 10,000 rows to prevent the "Blank Page" memory error
    df = pd.read_csv(file_path, nrows=10000)
    
    # FIX: Standardize column names to lowercase immediately
    df.columns = [str(c).lower().strip() for c in df.columns]
    
    # FIX: Rename common variations to 'latitude' and 'longitude'
    df = df.rename(columns={
        'lat': 'latitude', 
        'lon': 'longitude',
        'long': 'longitude',
        'primary_type': 'primary type'
    })
    
    # FIX: Remove rows with empty location data to prevent Map Crash
    df = df.dropna(subset=['latitude', 'longitude'])
    
    return df

try:
    df = load_data()
    st.success("Data loaded successfully!")
    
    # 3. Sidebar Filters
    st.sidebar.header("Filter Options")
    
    # SAFELY get the crime types
    if 'primary type' in df.columns:
        column_to_filter = 'primary type'
    elif 'category' in df.columns:
        column_to_filter = 'category'
    else:
        # Fallback if names are totally different
        column_to_filter = df.columns[1] 

    crime_types = df[column_to_filter].unique().tolist()
    selected_crime = st.sidebar.multiselect("Select Crime Type", crime_types, default=crime_types[:3])

    # 4. Filter the Data
    filtered_df = df[df[column_to_filter].isin(selected_crime)]

    # 5. Map Visualization
    st.subheader(f"Crime Hotspots: {', '.join(selected_crime[:2])}...")
    # This renders the map using the cleaned coordinates
    st.map(filtered_df)

    # 6. Summary Stats
    st.write(f"Showing **{len(filtered_df)}** incidents on the map.")

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
    st.info("Ensure your CSV has columns for Latitude and Longitude.")

# 7. Time Series Analysis (Trend Chart)
st.subheader("Crime Trends Over Time")

if 'date' in filtered_df.columns:
    try:
        # Convert date column to actual datetime objects
        filtered_df['date'] = pd.to_datetime(filtered_df['date'])
        
        # Group by date and count number of crimes
        # 'D' means daily. You can change to 'W' for weekly if it's too messy.
        crime_trend = filtered_df.resample('D', on='date').size().reset_index(name='Crime Count')
        
        # Display a Line Chart
        st.line_chart(data=crime_trend, x='date', y='Crime Count')
        
    except Exception as e:
        st.write("Could not generate trend chart. Ensure 'Date' column is formatted correctly.")
else:
    st.info("Date column not found. Add a 'Date' column to see trends over time.")

# 8. Category Breakdown (Bar Chart)
st.subheader("Crimes by Category")
category_counts = filtered_df[column_to_filter].value_counts()
st.bar_chart(category_counts)

# 9. Threat Density Heatmap
st.subheader("🔥 Threat Intensity Heatmap")
# We use Plotly's density map for a more 'cyber' feel
fig_heat = px.density_mapbox(
    filtered_df, 
    lat='latitude', 
    lon='longitude', 
    z=np.ones(len(filtered_df)), # Weight each point equally
    radius=10,
    center=dict(lat=filtered_df.latitude.mean(), lon=filtered_df.longitude.mean()),
    zoom=10,
    mapbox_style="carto-darkmatter" # Dark mode map
)
fig_heat.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig_heat, use_container_width=True)
