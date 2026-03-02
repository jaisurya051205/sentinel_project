from sklearn.cluster import KMeans
import pandas as pd

def detect_hotspots(df, n_clusters=10):
    # Filter for coordinates and remove missing values
    coords = df[['Latitude', 'Longitude']].dropna()
    
    # Initialize the AI Model (K-Means)
    # n_clusters=10 means the AI will find the 10 most 'active' centers
    model = KMeans(n_clusters=n_clusters, n_init=10)
    clusters = model.fit(coords)
    
    # Extract the center points (The 'Hotspots')
    hotspots = pd.DataFrame(clusters.cluster_centers_, columns=['lat', 'lon'])
    return hotspots
