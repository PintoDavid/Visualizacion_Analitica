from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import json
import os

app = Flask(__name__)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para procesar archivos JSON y BIN
@app.route('/procesar_archivos', methods=['POST'])
def procesar_archivos():
    json_file = request.files.get('json_file')
    bin_file = request.files.get('bin_file')
    
    if not json_file or not bin_file:
        return jsonify({'error': 'Ambos archivos deben ser cargados'}), 400

    # Cargar datos JSON
    json_data = json.load(json_file)
    df_json = pd.DataFrame(json_data)

    # Leer datos BIN como numpy array
    bin_data = np.frombuffer(bin_file.read(), dtype=np.uint8)
    df_json['bin_data'] = bin_data[:len(df_json)]  # Emparejar según longitud

    # K-means clustering
    X = df_json[['x', 'y']].dropna()  # Cambia 'x' e 'y' según tu estructura JSON
    n_clusters = 3  # Número de clusters para simplificar

    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(X)
    df_json['cluster'] = kmeans.labels_.tolist()

    # Formato de salida JSON
    result_data = df_json.to_dict(orient='records')
    return jsonify(result_data)

if __name__ == '__main__':
    app.run(debug=True)
