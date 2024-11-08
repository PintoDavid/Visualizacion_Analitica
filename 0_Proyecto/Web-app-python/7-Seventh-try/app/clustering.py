import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def perform_clustering(x_file, y_file, n_clusters):
    x_data = pd.read_json(x_file) if x_file.endswith('.json') else np.fromfile(x_file, dtype=np.float32)
    y_data = pd.read_json(y_file) if y_file.endswith('.json') else np.fromfile(y_file, dtype=np.float32)
    
    data = pd.DataFrame({'X': x_data, 'Y': y_data})
    kmeans = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=300, n_init=10, random_state=42)
    kmeans.fit(data)

    clusters = kmeans.labels_.tolist()
    centroids = kmeans.cluster_centers_.tolist()
    silhouette_avg = silhouette_score(data, clusters)

    return {
        'clusters': clusters,
        'centroids': centroids,
        'silhouette_score': silhouette_avg
    }
