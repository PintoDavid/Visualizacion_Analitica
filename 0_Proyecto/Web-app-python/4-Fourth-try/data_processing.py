import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import json

def process_data(file_path):
    # Leer el archivo según su extensión
    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
    elif file_path.endswith('.json'):
        with open(file_path, 'r') as f:
            data = pd.DataFrame(json.load(f))
    elif file_path.endswith('.bin'):
        data = pd.read_pickle(file_path)
    else:
        raise ValueError("Unsupported file type")

    # Aplicar K-means (con 3 clusters por defecto)
    X = data.dropna()
    kmeans = KMeans(n_clusters=3, init='k-means++', random_state=42)
    kmeans.fit(X)
    data['Cluster'] = kmeans.labels_

    return data.to_dict(orient='records')
