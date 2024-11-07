# AGREGAR PENIENTE
# CORREGIR ALETOREIDAD AL ACTUALIZAR VENTANA AL CAMBIAR OPCION COMO MOSTRAR GRAFICO DEL COEF VS K
# ADAPTARLO A LECTURA DE LOS BIN
# GUARDAR MEMORIA ULTIMO VALOR DE ALEATOREIDAD DEL PUNTO 2 PENDIENTE
# INTENTAR OPTIMIZAR LA MEMORIA IGNORANDO LOS MISMOS NUMEROS EN LAS MISMAS POCICIONES
# OPTIMIZAR MEMORIA IGNORANDO COLUMNAS SIN USAR
# INTENTAR OPTIMIZAR DATOS REPETIDOS AL MOMENTO DE INICIARLO CON LA LECTURA
import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog, Label, Button, StringVar, OptionMenu, Scale, Checkbutton, BooleanVar
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np

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
def graficar_con_kmeans_optimizado(ax, data, x_column, y_column, n_clusters, max_iter=300, n_init=10, cluster_seleccionado=None, porcentaje_reduccion=0):
    X = data[[x_column, y_column]].dropna()

    # Aplicar K-means con optimización
    kmeans = KMeans(
        n_clusters=n_clusters,
        init='k-means++',
        max_iter=max_iter,
        n_init=n_init,
        random_state=42
    )
    kmeans.fit(X)
    data['Cluster'] = kmeans.labels_

    # Limpiar el eje y graficar los datos
    ax.clear()

    # Generar colores diferentes para cada cluster
    colors = plt.cm.get_cmap('tab10', n_clusters)

    # Aplicar la reducción de datos si se especifica un porcentaje
    if porcentaje_reduccion > 0:
        # Reducir la cantidad de datos aleatoriamente por cluster
        for cluster in range(n_clusters):
            clustered_data = data[data['Cluster'] == cluster]
            n_reducidos = int(len(clustered_data) * (porcentaje_reduccion / 100))
            if n_reducidos > 0:
                clustered_data = clustered_data.sample(n=n_reducidos)  # Seleccionar aleatoriamente
            ax.scatter(clustered_data[x_column], clustered_data[y_column], color=colors(cluster), label=f'Cluster {cluster}', alpha=0.6)
    else:
        # Graficar todos los clusters sin reducción
        for cluster in range(n_clusters):
            clustered_data = data[data['Cluster'] == cluster]
            ax.scatter(clustered_data[x_column], clustered_data[y_column], color=colors(cluster), label=f'Cluster {cluster}', alpha=0.6)

    ax.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=100, c='black', marker='X', label='Centroides')
    ax.set_title(f'Gráfico de Clustering K-means Optimizado ({n_clusters} Clusters)')
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    ax.legend()
    ax.grid(True)

# Función para calcular coeficientes de silueta para múltiples valores de k
def calcular_coeficientes_silueta(data, x_column, y_column, max_k):
    coeficientes = []
    k_values = list(range(2, max_k + 1))  # Desde 2 hasta max_k

    for n_clusters in k_values:
        X = data[[x_column, y_column]].dropna()
        
        kmeans = KMeans(
            n_clusters=n_clusters,
            init='k-means++',
            max_iter=300,
            n_init=10,
            random_state=42
        )
        kmeans.fit(X)
        
        # Calcular el coeficiente de silueta
        silhouette_avg = silhouette_score(X, kmeans.labels_)
        coeficientes.append(silhouette_avg)

    return k_values, coeficientes

# Función para graficar coeficientes de silueta
def graficar_coeficientes_silueta(ax, k_values, coeficientes):
    ax.clear()
    ax.plot(k_values, coeficientes, marker='o')
    ax.set_title('Coeficiente de Silueta vs Número de Clusters')
    ax.set_xlabel('Número de Clusters (k)')
    ax.set_ylabel('Coeficiente de Silueta')
    ax.axhline(0, color='grey', lw=0.8, ls='--')
    ax.grid(True)

# Función para seleccionar columnas y definir número de clusters e iteraciones
def seleccionar_columnas_clusters_iteraciones(file_path):
    data = pd.read_csv(file_path)
    columnas = data.columns.tolist()
    
    root = Tk()
    root.title("Seleccionar Columnas, Clusters e Iteraciones")

    x_column = StringVar(root)
    y_column = StringVar(root)
    
    x_column.set(columnas[0])
    y_column.set(columnas[1] if len(columnas) > 1 else columnas[0])
    
    Label(root, text="Selecciona la columna para el eje X:").pack()
    OptionMenu(root, x_column, *columnas).pack()
    
    Label(root, text="Selecciona la columna para el eje Y:").pack()
    OptionMenu(root, y_column, *columnas).pack()

    # Slider para controlar el número de clusters (k)
    Label(root, text="Número de Clusters (k):").pack()
    k_slider = Scale(root, from_=2, to=10, orient='horizontal')  # Cambiado a 10 por la limitación de colores
    k_slider.set(3)  # Valor inicial
    k_slider.pack()
    
    # Slider para controlar el número de iteraciones
    Label(root, text="Número de Iteraciones:").pack()
    iter_slider = Scale(root, from_=10, to=1000, orient='horizontal')
    iter_slider.set(300)  # Valor inicial
    iter_slider.pack()

    # Checkbox para mostrar el coeficiente de silueta
    mostrar_coeficientes = BooleanVar()
    mostrar_coeficientes.set(False)
    Checkbutton(root, text="Mostrar gráfico de Coeficientes de Silueta", variable=mostrar_coeficientes).pack()

    # Checkbox para filtrar los clusters
    filtrar_cluster = BooleanVar()
    filtrar_cluster.set(False)
    Checkbutton(root, text="Filtrar por Cluster Seleccionado", variable=filtrar_cluster).pack()

    # Slider adicional para seleccionar el cluster
    cluster_slider = Scale(root, from_=0, to=9, orient='horizontal', state='disabled')  # Ajustar rango al máximo de clusters
    cluster_slider.pack()

    # Checkbox para habilitar la reducción de datos
    habilitar_reduccion = BooleanVar()
    habilitar_reduccion.set(False)
    Checkbutton(root, text="Habilitar Reducción de Datos por Cluster", variable=habilitar_reduccion).pack()

    # Slider para seleccionar el porcentaje de reducción
    Label(root, text="Porcentaje de Reducción:").pack()
    porcentaje_slider = Scale(root, from_=0, to=100, orient='horizontal', state='disabled')  # Inicialmente deshabilitado
    porcentaje_slider.pack()

    # Crear subgráficas para K-means y Coeficiente de Silueta
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    plt.ion()  # Activar modo interactivo

    # Función para actualizar las gráficas
    def actualizar_graficas(*args):
        n_clusters = k_slider.get()
        max_iter = iter_slider.get()
        
        # Actualizar el rango del slider de cluster
        cluster_slider.config(to=n_clusters - 1)  # Ajustar el to para que esté en el rango correcto

        cluster_seleccionado = cluster_slider.get() if filtrar_cluster.get() else None
        porcentaje_reduccion = porcentaje_slider.get() if habilitar_reduccion.get() else 0  # Obtener el porcentaje si está habilitado

        # Graficar K-means optimizado
        graficar_con_kmeans_optimizado(ax1, data, x_column.get(), y_column.get(), n_clusters, max_iter=max_iter, n_init=10, cluster_seleccionado=cluster_seleccionado, porcentaje_reduccion=porcentaje_reduccion)

        # Calcular y graficar coeficientes de silueta solo si el checkbox está activado
        if mostrar_coeficientes.get():
            k_values, coeficientes = calcular_coeficientes_silueta(data, x_column.get(), y_column.get(), n_clusters)
            graficar_coeficientes_silueta(ax2, k_values, coeficientes)

        plt.draw()  # Redibujar la figura

    # Asociar los sliders y los checkboxes a la función de actualización
    k_slider.bind("<Motion>", actualizar_graficas)
    iter_slider.bind("<Motion>", actualizar_graficas)
    mostrar_coeficientes.trace("w", actualizar_graficas)  # Actualizar al cambiar el checkbox
    cluster_slider.bind("<Motion>", actualizar_graficas)
    filtrar_cluster.trace("w", lambda *args: cluster_slider.config(state='normal' if filtrar_cluster.get() else 'disabled'))  # Habilitar/deshabilitar el slider de cluster
    habilitar_reduccion.trace("w", lambda *args: porcentaje_slider.config(state='normal' if habilitar_reduccion.get() else 'disabled'))  # Habilitar/deshabilitar el slider de porcentaje

    # Ejecutar la función al inicio
    actualizar_graficas()

    # Botón para cerrar la ventana
    Button(root, text="Cerrar", command=root.destroy).pack()
    
    plt.show()  # Mostrar la ventana de graficado
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
