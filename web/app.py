import streamlit as st
import pandas as pd
import pydeck as pdk
from sklearn.cluster import KMeans
import os

# --- 1. SYSTEM CONFIG & DATA ---
st.set_page_config(page_title="Sentinel AI Chicago", layout="wide")

if 'dispatch_logs' not in st.session_state:
    st.session_state.dispatch_logs = []
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

@st.cache_data
def load_data():
    FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw", "Crimes.csv")
    if not os.path.exists(FILE_PATH): FILE_PATH = "data/raw/Crimes.csv" 
    df = pd.read_csv(FILE_PATH, encoding='latin1').sample(n=50000, random_state=42)
    df['lat'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['lon'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['hour'] = df['Date'].dt.hour
    df['date_only'] = df['Date'].dt.date
    return df.dropna(subset=['lat', 'lon', 'Date'])

df = load_data()

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("🔐 Command Access")
    if not st.session_state.logged_in:
        pwd = st.text_input("Password", type="password")
        if st.button("Unlock"):
            if pwd == "admin":
                st.session_state.logged_in = True
                st.rerun()
    else:
        st.success("✅ Online")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
    st.markdown("---")
    selected_crimes = st.multiselect("Filter", sorted(df['Primary Type'].unique()), default=["ROBBERY", "BATTERY"])
    hour_range = st.slider("Time", 0, 23, (18, 2))
    map_mode = st.radio("Mode", ["2D Tactical", "3D Intelligence"])
    patrol_sensitivity = st.slider("AI Sensitivity", 10, 50, 20)

# --- 3. FILTERING ---
if hour_range[0] <= hour_range[1]:
    f_df = df[(df['hour'] >= hour_range[0]) & (df['hour'] <= hour_range[1])]
else:
    f_df = df[(df['hour'] >= hour_range[0]) | (df['hour'] <= hour_range[1])]
f_df = f_df[f_df['Primary Type'].isin(selected_crimes)]

# --- 4. TOP METRICS ---
st.title("🏙️ Sentinel: Tactical Command")
incident_count = len(f_df)
t_msg, t_col = ("🔴 CRITICAL", "red") if incident_count > 3000 else (("🟠 HIGH", "orange") if incident_count > 1500 else ("🔵 LOW", "blue"))

m1, m2, m3, m4 = st.columns(4)
m1.metric("Incidents", incident_count)
m2.markdown(f"**Threat:** :{t_col}[{t_msg}]")
m3.metric("Units Req.", int(incident_count / 75))
m4.metric("Status", "SECURE" if st.session_state.logged_in else "GUEST")

# --- 5. CENTER FEED (MAP + EXPANDED TREND) ---
col_main, col_dispatch = st.columns([2, 1])

with col_main:
    v_state = pdk.ViewState(latitude=41.8781, longitude=-87.6298, zoom=10, pitch=45 if "3D" in map_mode else 0)
    layer = pdk.Layer(
        'HexagonLayer' if "3D" in map_mode else 'ScatterplotLayer',
        f_df[['lon', 'lat']].to_dict('records'),
        get_position='[lon, lat]',
        get_color='[255, 30, 0, 140]',
        get_radius=120,
        radius_min_pixels=4,
        extruded=True if "3D" in map_mode else False,
        elevation_scale=100,
        pickable=True
    )
    st.pydeck_chart(pdk.Deck(map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json', initial_view_state=v_state, layers=[layer]), height=420)

    # --- CHART INCREASED TO FILL SPACE ---
    st.subheader("📈 Incident Trend Analysis")
    if not f_df.empty:
        trend_data = f_df.groupby('date_only').size().reset_index(name='Incidents')
        # Increased height to 500 to kill the empty space shown in screenshot
        st.line_chart(trend_data.set_index('date_only'), height=500)

with col_dispatch:
    st.subheader("📍 High-Risk Zones")
    hotspots = f_df['Block'].value_counts().head(5).reset_index()
    hotspots.columns = ['Block', 'Count']
    for _, row in hotspots.iterrows():
        st.error(f"**{row['Block']}** ({row['Count']} Events)")
    
    st.markdown("---")
    st.subheader("📡 Dispatch Command")
    target_block = st.selectbox("Select Block", hotspots['Block'].tolist() if not hotspots.empty else ["No Data"])
    priority = st.select_slider("Set Priority Level", options=["Routine", "High", "Urgent"], value="Routine")
    p_color = {"Urgent": "🔴", "High": "🟠", "Routine": "⚪"}
    
    dispatch_note = st.text_area("Operational Instructions", height=150)
    if st.button("Log Dispatch Orders"):
        if dispatch_note:
            st.session_state.dispatch_logs.insert(0, {
                "Priority": f"{p_color[priority]} {priority}",
                "Time": pd.Timestamp.now().strftime('%H:%M:%S'),
                "Block": target_block,
                "Orders": dispatch_note
            })
            st.toast(f"{priority} Order Broadcasted.")

# --- 6. FOOTER ---
st.markdown("---")
bot_left, bot_right = st.columns(2)

with bot_left:
    st.subheader("🔐 AI Tactical Patrol Zones")
    if st.session_state.logged_in and not f_df.empty:
        kmeans = KMeans(n_clusters=patrol_sensitivity, n_init=10).fit(f_df[['lat', 'lon']])
        dispatch_df = pd.DataFrame(kmeans.cluster_centers_, columns=['lat', 'lon'])
        st.pydeck_chart(pdk.Deck(
            map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
            initial_view_state=v_state, 
            layers=[pdk.Layer('ScatterplotLayer', dispatch_df.to_dict('records'), get_position='[lon, lat]', get_color='[0, 150, 255, 200]', get_radius=500, radius_min_pixels=8)]
        ), height=300)

with bot_right:
    st.subheader("📝 Searchable Shift Logs")
    search_query = st.text_input("🔍 Search Logs...", "").lower()
    if st.session_state.dispatch_logs:
        log_df = pd.DataFrame(st.session_state.dispatch_logs)
        filtered_logs = log_df[log_df.apply(lambda row: search_query in row.astype(str).str.lower().values, axis=1)]
        st.table(filtered_logs)
    
    if st.button("🗑️ Clear All Logs"):
        st.session_state.dispatch_logs = []
        st.rerun()
