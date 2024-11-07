import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog, Label, Button, StringVar, OptionMenu, simpledialog
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score  # Importar para calcular el coeficiente de silueta

# Función para seleccionar la carpeta con archivos CSV
def seleccionar_carpeta_csv():
    carpeta_codigo = os.path.dirname(os.path.abspath(__file__))
    archivos_csv = [os.path.join(carpeta_codigo, file) for file in os.listdir(carpeta_codigo) if file.endswith('.csv')]
    
    if not archivos_csv:
        root = Tk()
        root.withdraw()
        carpeta_seleccionada = filedialog.askdirectory(title="Selecciona la carpeta con archivos CSV")
        root.destroy()
        
        if carpeta_seleccionada:
            archivos_csv = [os.path.join(carpeta_seleccionada, file) for file in os.listdir(carpeta_seleccionada) if file.endswith('.csv')]
    
    return archivos_csv

# Función para aplicar K-means optimizado y graficar
def graficar_con_kmeans_optimizado(file_path, x_column, y_column, n_clusters, max_iter=300, n_init=10):
    # Leer el archivo CSV
    data = pd.read_csv(file_path)
    # Seleccionar las columnas
    X = data[[x_column, y_column]].dropna()  # Eliminar filas con valores nulos
    
    # Aplicar K-means con optimización
    kmeans = KMeans(
        n_clusters=n_clusters,
        init='k-means++',       # Inicialización optimizada
        max_iter=max_iter,      # Límite de iteraciones
        n_init=n_init,          # Número de inicios para buscar mejor agrupación
        random_state=42         # Asegura resultados reproducibles
    )
    kmeans.fit(X)
    data['Cluster'] = kmeans.labels_
    
    # Calcular el coeficiente de silueta
    silhouette_avg = silhouette_score(X, data['Cluster'])
    
    # Graficar los datos con los clusters
    plt.figure(figsize=(10, 6))
    for cluster in range(n_clusters):
        clustered_data = data[data['Cluster'] == cluster]
        plt.scatter(clustered_data[x_column], clustered_data[y_column], label=f'Cluster {cluster}', alpha=0.6)
    
    plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=100, c='black', marker='X', label='Centroides')
    plt.title(f'Gráfico de Clustering K-means Optimizado ({n_clusters} Clusters)')
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.legend()
    plt.grid(True)
    
    # Mostrar el coeficiente de silueta en la gráfica
    plt.text(0.05, 0.95, f'Coeficiente de Silueta: {silhouette_avg:.2f}', transform=plt.gca().transAxes,
             fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', edgecolor='black', facecolor='white'))
    
    plt.show()

# Función para seleccionar columnas y definir número de clusters e iteraciones
def seleccionar_columnas_clusters_iteraciones(file_path):
    # Leer el archivo CSV para obtener columnas
    data = pd.read_csv(file_path)
    columnas = data.columns.tolist()
    
    root = Tk()
    root.title("Seleccionar Columnas, Clusters e Iteraciones")

    # Variables para almacenar las selecciones de columnas
    x_column = StringVar(root)
    y_column = StringVar(root)
    
    x_column.set(columnas[0])
    y_column.set(columnas[1] if len(columnas) > 1 else columnas[0])
    
    # Etiquetas y menús desplegables para seleccionar columnas
    Label(root, text="Selecciona la columna para el eje X:").pack()
    OptionMenu(root, x_column, *columnas).pack()
    
    Label(root, text="Selecciona la columna para el eje Y:").pack()
    OptionMenu(root, y_column, *columnas).pack()
    
    # Función para pedir número de clusters e iteraciones y aplicar K-means
    def solicitar_parametros():
        # Pedir el número de clusters
        n_clusters = simpledialog.askinteger("K-means Clusters", "Ingrese el número de clusters para K-means:", minvalue=1, maxvalue=20)
        
        # Pedir el número máximo de iteraciones
        max_iter = simpledialog.askinteger("Iteraciones", "Ingrese el número máximo de iteraciones:", minvalue=10, maxvalue=1000)
        
        # Si ambos valores se han definido, aplicar K-means y graficar
        if n_clusters and max_iter:
            graficar_con_kmeans_optimizado(file_path, x_column.get(), y_column.get(), n_clusters, max_iter=max_iter, n_init=10)
        
        root.destroy()
    
    # Botón para abrir la ventana de parámetros
    Button(root, text="Aplicar K-means y Graficar", command=solicitar_parametros).pack()
    root.mainloop()

# Obtener la lista de archivos CSV en la carpeta del código o en la seleccionada
archivos_csv = seleccionar_carpeta_csv()

if archivos_csv:
    print("\nArchivos CSV encontrados:")
    for idx, archivo in enumerate(archivos_csv, 1):
        print(f"{idx}. {archivo}")

    archivo_a_graficar = archivos_csv[0]
    print(f"\nAbriendo interfaz para seleccionar columnas, clusters e iteraciones en el archivo: {archivo_a_graficar}")
    
    # Llamar a la función para seleccionar columnas, clusters e iteraciones y aplicar K-means
    seleccionar_columnas_clusters_iteraciones(archivo_a_graficar)
else:
    print("No se encontraron archivos CSV en la carpeta especificada.")
