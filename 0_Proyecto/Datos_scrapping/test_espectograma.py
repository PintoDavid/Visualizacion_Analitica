import os
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Configuración de la carpeta que contiene los archivos
DIRECTORY = "D:/DAVID/Git-projects/Visualizacion_analitica/0_Proyecto/Datos_scrapping/covis_data_cloned/001/descompresion tar"  # Cambia esto a la ruta de tu carpeta con archivos JSON y BIN

# Crear espectrograma
def create_spectrogram(data, ax):
    f, t, Sxx = signal.spectrogram(data, fs=1000)  # Suponiendo que fs=1000 Hz
    ax.clear()  # Limpiar el eje antes de graficar
    ax.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
    ax.set_ylabel('Frecuencia [Hz]')
    ax.set_xlabel('Tiempo [sec]')
    plt.pause(0.1)  # Pausa para actualizar la figura

# Procesar archivos JSON y BIN
def process_files_and_create_spectrograms(directory):
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.ion()  # Habilitar modo interactivo

    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as json_file:
                        data = json.load(json_file)
                        # Asumiendo que el JSON tiene la clave 'data'
                        if 'data' in data:
                            print(f"Procesando archivo JSON: {file_path}")
                            create_spectrogram(np.array(data['data']), ax)

                elif file.endswith('.bin'):
                    file_path = os.path.join(root, file)
                    data = np.fromfile(file_path, dtype=np.float32)  # Cambiar dtype según tu archivo
                    print(f"Procesando archivo BIN: {file_path}")
                    create_spectrogram(data, ax)

    except Exception as e:
        print(f"Ocurrió un error al procesar los archivos: {e}")

    plt.show()  # Mostrar la figura final

# Función principal
def main():
    process_files_and_create_spectrograms(DIRECTORY)

# Ejecutar el programa
if __name__ == "__main__":
    main()
