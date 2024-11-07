import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import threading
import json

# Configuración de la carpeta que contiene los archivos
DIRECTORY = "D:/DAVID/Git-projects/Visualizacion_analitica/0_Proyecto/Datos_scrapping/covis_data_cloned/001/descompresion tar"

# Inicializar variables globales
data_buffers = []
bin_file_names = []
json_file_names = []
fig, ax = None, None  # Declarar como global
load_lock = threading.Lock()  # Para manejar el acceso concurrente a los datos

# Variables para limitar la cantidad de archivos
MAX_FILES = 5  # Cambia esto a la cantidad máxima deseada
LIMIT_FILES = True  # Cambia a False para cargar todos los archivos

# Cargar archivos BIN y JSON
def load_bin_and_json_files(directory):
    file_count = 0  # Contador de archivos cargados
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.bin'):
                file_path = os.path.join(root, file)
                bin_file_names.append(file)  # Agregar nombre de archivo
                data_buffers.append(np.fromfile(file_path, dtype=np.float32))  # Leer y almacenar datos
                json_file_name = file.replace('.bin', '.json')  # Suponiendo que el JSON tiene el mismo nombre que el BIN
                json_file_path = os.path.join(root, json_file_name)
                if os.path.exists(json_file_path):
                    json_file_names.append(json_file_path)  # Agregar la ruta del JSON
                else:
                    json_file_names.append(None)  # Si no hay JSON, agregar None
                
                file_count += 1  # Incrementar contador de archivos
                # Si se ha alcanzado el límite, salir del bucle
                if LIMIT_FILES and file_count >= MAX_FILES:
                    return

# Crear gráfico de líneas
def plot_data(ax, data, title, json_data=None):
    ax.clear()  # Limpiar el eje antes de graficar
    ax.plot(data, color='blue', label='Datos de Frecuencia')  # Graficar los datos en un gráfico de líneas
    ax.set_title(title)  # Cambiar el título
    ax.set_xlabel('Índice')
    ax.set_ylabel('Valor de Frecuencia')
    ax.grid()

    # Si hay datos JSON, añadir anotaciones
    if json_data:
        for event in json_data.get('events', []):
            x_coord = event['time']  # Obtener la coordenada del evento
            if 0 <= x_coord < len(data):  # Verificar que la coordenada esté dentro de los límites
                y_value = data[x_coord]  # Obtener el valor de la frecuencia en ese índice
                ax.scatter(x_coord, y_value, color='red', s=100, zorder=5)  # Dibujar un punto en la gráfica
                ax.annotate('Evento', xy=(x_coord, y_value), xytext=(x_coord, y_value * 1.2),
                            arrowprops=dict(facecolor='black', arrowstyle='->'))

    plt.draw()  # Actualizar la figura

# Función para actualizar el gráfico al mover el slider
def update(val):
    index = int(val)  # Obtener el índice del slider
    with load_lock:  # Usar el lock para asegurar acceso seguro
        # Cargar datos JSON si están disponibles
        json_data = None
        if json_file_names[index]:
            with open(json_file_names[index], 'r') as json_file:
                json_data = json.load(json_file)

        plot_data(ax, data_buffers[index], bin_file_names[index], json_data)  # Actualizar los datos y el título

# Cargar los archivos BIN y JSON en un hilo separado
def load_files_thread():
    load_bin_and_json_files(DIRECTORY)

# Función principal
def main():
    global fig, ax  # Hacer fig y ax globales

    # Inicializar la figura y los ejes antes de la carga de archivos
    fig, ax = plt.subplots(figsize=(12, 6))
    plt.subplots_adjust(bottom=0.25)  # Hacer espacio para el slider

    # Iniciar la carga de archivos en un hilo separado
    loader_thread = threading.Thread(target=load_files_thread)
    loader_thread.start()

    # Esperar a que al menos un archivo se cargue antes de graficar
    loader_thread.join()

    if len(data_buffers) < 1:
        print("No se encontraron archivos BIN para visualizar.")
        plt.close(fig)  # Cerrar la ventana si no hay archivos
        return

    # Graficar los datos del primer archivo
    json_data = None
    if json_file_names[0]:
        with open(json_file_names[0], 'r') as json_file:
            json_data = json.load(json_file)

    plot_data(ax, data_buffers[0], bin_file_names[0], json_data)

    # Configurar slider
    ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03])  # Posición del slider
    slider = Slider(ax_slider, 'Archivo', 0, len(data_buffers) - 1, valinit=0, valstep=1)  # Usar el número de archivos cargados

    # Conectar el slider con la función de actualización
    slider.on_changed(update)

    # Comenzar a cargar los archivos restantes en segundo plano
    loader_thread.join()  # Esperar a que el hilo termine para asegurar que los datos estén disponibles
    plt.show()

# Ejecutar el programa
if __name__ == "__main__":
    main()
