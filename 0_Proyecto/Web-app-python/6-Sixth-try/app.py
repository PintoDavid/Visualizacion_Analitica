import os
import json
import numpy as np
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, send_from_directory, jsonify
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

app = Flask(__name__)

# Directorio donde se guardarán las imágenes generadas
IMAGE_FOLDER = 'static/images'
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# Función para leer datos de archivo BIN
def leer_binario(archivo):
    return np.fromfile(archivo, dtype=np.float64)  # Ajusta el tipo de dato según tu archivo BIN

# Función para leer datos de archivo JSON
def leer_json(archivo):
    with open(archivo, 'r') as f:
        return json.load(f)

# Función para procesar y graficar
def graficar_con_kmeans(data_x, data_y, n_clusters, max_iter=300, n_init=10):
    # Asegurar que no haya valores nulos
    data = pd.DataFrame({'X': data_x, 'Y': data_y}).dropna()

    # Aplicar K-means
    kmeans = KMeans(
        n_clusters=n_clusters,
        init='k-means++',
        max_iter=max_iter,
        n_init=n_init,
        random_state=42
    )
    kmeans.fit(data[['X', 'Y']])
    data['Cluster'] = kmeans.labels_

    # Crear gráfico
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = plt.cm.get_cmap('tab10', n_clusters)

    for cluster in range(n_clusters):
        clustered_data = data[data['Cluster'] == cluster]
        ax.scatter(clustered_data['X'], clustered_data['Y'], color=colors(cluster), label=f'Cluster {cluster}', alpha=0.6)

    ax.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=100, c='black', marker='X', label='Centroides')
    ax.set_title(f'Clustering K-means ({n_clusters} Clusters)')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.legend()
    ax.grid(True)

    # Guardar el gráfico como imagen
    image_path = os.path.join(IMAGE_FOLDER, 'kmeans_plot.png')
    plt.savefig(image_path)
    plt.close()
    
    return 'kmeans_plot.png'  # Retornar el nombre del archivo generado

# Ruta para la página principal
@app.route('/')
def index():
    archivos = obtener_archivos()
    return render_template('index.html', archivos=archivos)

# Función para obtener archivos en la carpeta
def obtener_archivos():
    carpeta_codigo = os.path.dirname(os.path.abspath(__file__))
    archivos = [os.path.join(carpeta_codigo, file) for file in os.listdir(carpeta_codigo) if file.endswith('.bin') or file.endswith('.json')]
    return archivos

# Ruta para cargar archivos seleccionados
@app.route('/upload', methods=['POST'])
def upload_file():
    archivo_index = int(request.form['archivo_index'])
    archivos = obtener_archivos()
    archivo_seleccionado = archivos[archivo_index]
    
    if archivo_seleccionado.endswith('.bin'):
        data = leer_binario(archivo_seleccionado)
    elif archivo_seleccionado.endswith('.json'):
        data = leer_json(archivo_seleccionado)

    # Extraer fecha o nombre del archivo
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_archivo = os.path.basename(archivo_seleccionado)

    return render_template('configure.html', archivo=nombre_archivo, fecha=fecha, archivo_index=archivo_index, archivos=archivos, data=data)

# Ruta para procesar K-means y mostrar el gráfico
@app.route('/process', methods=['POST'])
def process_kmeans():
    archivo_index = int(request.form['archivo_index'])
    eje_x_tipo = request.form['eje_x_tipo']
    eje_y_tipo = request.form['eje_y_tipo']
    n_clusters = int(request.form['n_clusters'])

    archivos = obtener_archivos()
    archivo_seleccionado = archivos[archivo_index]

    # Leer los archivos según el tipo seleccionado para X e Y
    if eje_x_tipo == 'bin':
        data_x = leer_binario(archivo_seleccionado)
    elif eje_x_tipo == 'json':
        data_x = leer_json(archivo_seleccionado)

    if eje_y_tipo == 'bin':
        data_y = leer_binario(archivo_seleccionado)
    elif eje_y_tipo == 'json':
        data_y = leer_json(archivo_seleccionado)

    # Ejecutar K-means y graficar
    image_file = graficar_con_kmeans(data_x, data_y, n_clusters)

    # Retornar la imagen generada
    return jsonify({'image_url': f'/static/images/{image_file}'})


# Ruta para servir las imágenes generadas
@app.route('/static/images/<filename>')
def send_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)


if __name__ == '__main__':
    app.run(debug=True)
