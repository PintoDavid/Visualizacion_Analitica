import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog, Label, Button, StringVar, OptionMenu, Scale, Checkbutton, BooleanVar
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np

# Función para seleccionar la carpeta con archivos
def seleccionar_carpeta():
    # Seleccionar carpeta y normalizar la ruta
    root = Tk()
    root.withdraw()
    carpeta_seleccionada = filedialog.askdirectory(title="Selecciona la carpeta con archivos")
    root.destroy()
    
    if carpeta_seleccionada:
        carpeta_seleccionada = os.path.normpath(carpeta_seleccionada)  # Normalizar la ruta seleccionada
    return carpeta_seleccionada

# Función para listar archivos .csv, .json y .bin en la carpeta seleccionada
def listar_archivos(carpeta):
    archivos = []
    if carpeta and os.path.isdir(carpeta):
        # Recorrer archivos en la carpeta y seleccionar solo los que tengan las extensiones adecuadas
        archivos = [os.path.join(carpeta, file) for file in os.listdir(carpeta) if file.endswith(('.csv', '.json', '.bin'))]
    return archivos

# Función para cargar los datos según el tipo de archivo
def cargar_datos(archivo):
    # Cargar datos en función de la extensión del archivo
    if archivo.endswith('.csv'):
        data = pd.read_csv(archivo)
    elif archivo.endswith('.json'):
        data = pd.read_json(archivo)
    elif archivo.endswith('.bin'):
        # Aquí iría el código para leer archivos bin personalizados
        # data = ... (lectura de archivo bin)
        pass
    else:
        data = pd.DataFrame()  # Si el archivo no es de los tipos aceptados, devolver un DataFrame vacío
    return data

# Función para graficar usando K-means optimizado y mostrar en la interfaz de usuario
def graficar_kmeans(data, x_column, y_column, n_clusters, max_iter=300, n_init=10):
    # Implementación del clustering y graficado
    if not data.empty and x_column in data.columns and y_column in data.columns:
        X = data[[x_column, y_column]].dropna()
        kmeans = KMeans(n_clusters=n_clusters, max_iter=max_iter, n_init=n_init, random_state=42)
        kmeans.fit(X)
        data['Cluster'] = kmeans.labels_
        
        fig, ax = plt.subplots()
        colors = plt.cm.get_cmap('tab10', n_clusters)
        
        for cluster in range(n_clusters):
            clustered_data = data[data['Cluster'] == cluster]
            ax.scatter(clustered_data[x_column], clustered_data[y_column], color=colors(cluster), label=f'Cluster {cluster}')
        
        ax.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=100, c='black', marker='X', label='Centroides')
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)
        ax.legend()
        plt.show()

# Función principal para ejecutar la aplicación de clustering
def ejecutar_app():
    carpeta = seleccionar_carpeta()
    archivos = listar_archivos(carpeta)
    
    if archivos:
        for archivo in archivos:
            print(f"Procesando archivo: {archivo}")
            data = cargar_datos(archivo)
            if not data.empty:
                # Seleccionar columnas, número de clusters, etc.
                # Aquí se usarían controles de interfaz para elegir columnas y parámetros
                x_column = data.columns[0]  # Seleccionar primera columna como ejemplo
                y_column = data.columns[1] if len(data.columns) > 1 else x_column
                n_clusters = 3  # Ejemplo de cantidad de clusters
                
                # Graficar clustering con K-means
                graficar_kmeans(data, x_column, y_column, n_clusters)
    else:
        print("No se encontraron archivos compatibles en la carpeta seleccionada.")

# Ejecutar la aplicación
if __name__ == "__main__":
    ejecutar_app()
