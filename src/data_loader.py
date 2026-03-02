import streamlit as st
import pandas as pd
import pydeck as pdk
import os
import glob
import sys

# --- MAC PATH FIX ---
# This ensures the app always knows where the root folder is
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

try:
    from src.analytics_engine import detect_hotspots
except ImportError:
    st.error("Could not find analytics_engine.py in src folder!")

# --- PAGE CONFIG ---
st.set_page_config(page_title="Sentinel: Law Enforcement Portal", page_icon="👮", layout="wide")

# --- REGION CONFIGURATION ---
REGIONS = {
    "Chicago, USA": {
        "lat": 41.8781, "lon": -87.6298, "zoom": 10, 
        "file_pattern": os.path.join(ROOT_DIR, "data", "raw", "crimes.csv"),
        "map_style": 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json'
    },
    "Tamil Nadu, India": {
        "lat": 11.1271, "lon": 78.6569, "zoom": 7, 
        "file_pattern": os.path.join(ROOT_DIR, "data", "raw", "tn*.csv"), # FIXED PATH
        "map_style": 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json'
    }
}

# --- DATA ENGINE ---
@st.cache_data
def load_and_merge_data(pattern):
    files = glob.glob(pattern)
    if not files:
        return pd.DataFrame()
    
    df_list = []
    for f in files:
        temp_df = pd.read_csv(f)
        # Auto-detect category from filename (e.g., tnrobbery -> ROBBERY)
        fname = os.path.basename(f)
        category = fname.replace('tn', '').replace('.csv', '').upper()
        temp_df['Primary Type'] = category
        df_list.append(temp_df)
    
    return pd.concat(df_list, axis=0, ignore_index=True)

# --- AUTHENTICATION ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- SIDEBAR ---
st.sidebar.title("🌍 Global Command")
selected_name = st.sidebar.selectbox("Select Operations Area", list(REGIONS.keys()))
config = REGIONS[selected_name]

if not st.session_state.authenticated:
    with st.sidebar.form("login"):
        uid = st.text_input("Officer ID", type="password")
        if st.form_submit_button("Login"):
            if uid == "CPD2024":
                st.session_state.authenticated = True
                st.rerun()
else:
    if st.sidebar.button("🔓 Logout"):
        st.session_state.authenticated = False
        st.rerun()

# --- LOAD AND PROCESS ---
df = load_and_merge_data(config["file_pattern"])

if not df.empty and selected_name == "Tamil Nadu, India":
    tn_districts = {
        'ARIYALUR': [11.1401, 79.0747], 'CHENNAI': [13.0827, 80.2707],
        'COIMBATORE': [11.0168, 76.9558], 'CUDDALORE': [11.7480, 79.7714],
        'MADURAI': [9.9252, 78.1198], 'DINDIGUL': [10.3673, 77.9803]
    }
    col = 'District' if 'District' in df.columns else 'Unit'
    if col in df.columns:
        df['District_Clean'] = df[col].astype(str).str.upper()
        df['Latitude'] = df['District_Clean'].map(lambda x: tn_districts.get(x, [11.12, 78.65])[0])
        df['Longitude'] = df['District_Clean'].map(lambda x: tn_districts.get(x, [11.12, 78.65])[1])

# --- DISPLAY ---
st.title(f"Sentinel: {selected_name}")

if df.empty:
    # This helps you debug exactly where the app is looking
    st.error(f"Files not found at: {config['file_pattern']}")
    st.info("Current Working Directory: " + os.getcwd())
else:
    st.subheader("🏙️ Public Density Overview")
    st.pydeck_chart(pdk.Deck(
        map_style=config["map_style"],
        initial_view_state=pdk.ViewState(latitude=config["lat"], longitude=config["lon"], zoom=config["zoom"], pitch=45),
        layers=[pdk.Layer('HexagonLayer', data=df, get_position='[Longitude, Latitude]', radius=15000 if "Tamil" in selected_name else 200, elevation_scale=50, extruded=True)]
    ))

    if st.session_state.authenticated:
        st.markdown("---")
        st.header("🚨 AI Patrol Intelligence")
        
        # CREATE HOTSPOTS SAFELY
        if 'hotspots' not in st.session_state or st.sidebar.button("🔄 Refresh AI"):
             st.session_state.hotspots = detect_hotspots(df, n_clusters=5)
        
        st.pydeck_chart(pdk.Deck(
            map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
            initial_view_state=pdk.ViewState(latitude=config["lat"], longitude=config["lon"], zoom=config["zoom"]+1),
            layers=[pdk.Layer('ScatterplotLayer', data=st.session_state.hotspots, get_position='[lon, lat]', get_color='[0, 255, 255, 255]', get_radius=20000 if "Tamil" in selected_name else 500)]
        ))
