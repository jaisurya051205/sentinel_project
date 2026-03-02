import streamlit as st
import pandas as pd

# Use @st.cache_data so it only loads the file ONCE
@st.cache_data
def load_data():
    # Loading only 5,000 rows ensures the app never goes blank due to memory
    return pd.read_csv('data/raw/Crimes.csv', nrows=5000)

df = load_data()
st.title("Sentinel Project")
st.write("Data loaded successfully!")
st.map(df)
