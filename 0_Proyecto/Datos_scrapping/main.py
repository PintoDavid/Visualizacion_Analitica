import subprocess
import sys
import os
import tarfile
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from bs4 import BeautifulSoup
from tqdm import tqdm
import requests
import tkinter as tk
import time
from tkinter import ttk
from threading import Thread, Lock

# URL base
BASE_URL = "http://piweb.ooirsn.uw.edu/covis/data/BROWSE/2023/"

# Archivos de configuración
PROGRESS_FILE = "download_progress.resume"
IGNORE_FOLDERS_FILE = "ignore_folders.txt"
IGNORE_FILES_FILE = "ignore_files.txt"
LOCAL_DIR = "covis_data_cloned"  # Directorio de almacenamiento local

# Crear un lock para manejar el acceso a datos compartidos
lock = Lock()

# Función para instalar o actualizar bibliotecas necesarias
def install_packages(packages):
    for package in packages:
        try:
            __import__(package)
            print(f"{package} ya está instalado.")
        except ImportError:
            print(f"Instalando {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        else:
            print(f"Actualizando {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', package])

# Pausar y esperar la confirmación del usuario
def wait_for_user_or_timeout(timeout=5):
    print(f"Esperando {timeout} segundos... (presiona Enter para continuar antes)")
    for i in range(timeout):
        if i % 1 == 0:  # Mostrar el tiempo restante
            print(f"{timeout - i} segundos restantes.")
        time.sleep(1)
    input("Presiona Enter para continuar...")

# Generar archivos de configuración
def generate_config_files():
    # Ignorar carpetas
    with open(IGNORE_FOLDERS_FILE, 'w') as f:
        f.write("001\n002\n")  # Ejemplo de carpetas a ignorar

    # Ignorar archivos
    with open(IGNORE_FILES_FILE, 'w') as f:
        f.write("")  # Inicialmente vacío

    print(f"Archivos de configuración generados: {IGNORE_FOLDERS_FILE}, {IGNORE_FILES_FILE}")

# Cargar el progreso desde el archivo
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return set(f.read().splitlines())
    return set()

# Guardar el progreso en el archivo
def save_progress(downloaded_files):
    with open(PROGRESS_FILE, 'w') as f:
        f.write("\n".join(downloaded_files))

# Leer las carpetas a ignorar
def load_ignore_folders():
    if os.path.exists(IGNORE_FOLDERS_FILE):
        with open(IGNORE_FOLDERS_FILE, 'r') as f:
            return set(f.read().splitlines())
    return set()

# Leer las palabras a ignorar en los nombres de los archivos
def load_ignore_files():
    if os.path.exists(IGNORE_FILES_FILE):
        with open(IGNORE_FILES_FILE, 'r') as f:
            return set(f.read().splitlines())
    return set()

# Verificar si un archivo ya está completo
def is_file_complete(output_path, file_size):
    if os.path.exists(output_path):
        local_size = os.path.getsize(output_path)
        return local_size == file_size  # Comparar el tamaño local con el tamaño en el servidor
    return False

# Descargar archivos uno por uno
def download_file(url, output_path, downloaded_files):
    try:
        # Verificar si el archivo ya está descargado
        head_response = requests.head(url)
        file_size = int(head_response.headers.get('content-length', 0))  # Obtener el tamaño

        if is_file_complete(output_path, file_size):
            print(f"Ya descargado: {output_path}")
            with lock:
                downloaded_files.add(output_path)  # Añadir al progreso
                save_progress(downloaded_files)  # Guardar progreso
            return

        os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Crear directorios si no existen

        # Obtener el tamaño local del archivo para reanudar descarga si es posible
        local_size = 0
        if os.path.exists(output_path):
            local_size = os.path.getsize(output_path)

        headers = {"Range": f"bytes={local_size}-"} if local_size > 0 else None
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()  # Verificar si la solicitud fue exitosa

        # Descargar el archivo (o continuar si es parcial)
        mode = 'ab' if local_size > 0 else 'wb'  # 'ab' para agregar, 'wb' para nuevo archivo
        with open(output_path, mode) as file:
            with tqdm(total=file_size, initial=local_size, unit='B', unit_scale=True, desc=output_path.split('/')[-1]) as file_bar:
                for data in response.iter_content(1024):
                    file.write(data)
                    file_bar.update(len(data))

        print(f"Descargado: {output_path}")
        with lock:
            downloaded_files.add(output_path)  # Añadir al progreso
            save_progress(downloaded_files)  # Guardar progreso

    except Exception as e:
        print(f"Error al descargar {output_path}: {e}")

# Descomprimir archivos .tar.gz
def extract_file(file_path):
    try:
        extract_dir = file_path.replace('.tar.gz', '')
        os.makedirs(extract_dir, exist_ok=True)

        with tarfile.open(file_path, 'r:gz') as tar:
            tar.extractall(path=extract_dir)
        print(f"Extraído: {file_path} en {extract_dir}")
        return extract_dir

    except Exception as e:
        print(f"Error al extraer {file_path}: {e}")
        return None

# Scraping dinámico para descargar archivos
def scrape_and_download_files(base_url, current_dir, downloaded_files, ignore_folders, ignore_files):
    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Verificar si la solicitud fue exitosa
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')

        # Recorrer los enlaces para buscar archivos
        for link in links:
            href = link.get('href')
            # Ignorar carpetas según la lista
            if any(folder in href for folder in ignore_folders):
                print(f"Ignorando carpeta: {href}")
                continue
            
            if href.endswith('/'):  # Si es un directorio
                new_dir = os.path.join(current_dir, href)
                # Llamar recursivamente para explorar la subcarpeta
                scrape_and_download_files(base_url + href, new_dir, downloaded_files, ignore_folders, ignore_files)
            elif href.endswith('.tar.gz'):  # Si es un archivo .tar.gz
                file_url = base_url + href
                output_path = os.path.join(current_dir, href)

                # Descargar inmediatamente
                download_file(file_url, output_path, downloaded_files)

            # Ignorar archivos que contengan palabras específicas
            if any(word in href for word in ignore_files):
                print(f"Ignorando archivo: {href}")
                continue

    except Exception as e:
        print(f"No se pudo conectar a: {base_url} - Error: {e}")

# Procesar archivos JSON y BIN
def process_files_and_create_spectrograms(directory, ax):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as json_file:
                    data = json.load(json_file)
                    # Asumiendo que el JSON tiene la clave 'data'
                    if 'data' in data:
                        create_spectrogram(np.array(data['data']), ax)
            elif file.endswith('.bin'):
                file_path = os.path.join(root, file)
                data = np.fromfile(file_path, dtype=np.float32)  # Cambiar dtype según tu archivo
                create_spectrogram(data, ax)

# Crear espectrograma
def create_spectrogram(data, ax):
    f, t, Sxx = signal.spectrogram(data, fs=1000)  # Suponiendo que fs=1000 Hz
    ax.clear()  # Limpiar el eje antes de graficar
    ax.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
    ax.set_ylabel('Frecuencia [Hz]')
    ax.set_xlabel('Tiempo [sec]')
    plt.pause(0.1)  # Pausa para actualizar la figura

# Función para actualizar la ventana
def update_window():
    while True:
        time.sleep(5)  # Actualizar cada 5 segundos
        with lock:
            downloaded_files_copy = list(downloaded_files)  # Copia para evitar conflictos
        for downloaded_file in downloaded_files_copy:
            if downloaded_file.endswith('.tar.gz'):
                extract_dir = extract_file(downloaded_file)  # Extraer el archivo
                if extract_dir:
                    process_files_and_create_spectrograms(extract_dir, ax)  # Procesar archivos en el directorio extraído

# Función principal
def main():
    required_packages = ['requests', 'bs4', 'numpy', 'matplotlib', 'scipy', 'tqdm']
    install_packages(required_packages)

    wait_for_user_or_timeout()

    # Paso 2: Generar archivos de configuración
    print("Paso 2: Generando archivos de configuración.")
    generate_config_files()
    wait_for_user_or_timeout()

    # Crear directorio local
    os.makedirs(LOCAL_DIR, exist_ok=True)

    # Cargar carpetas y archivos a ignorar
    ignore_folders = load_ignore_folders()
    ignore_files = load_ignore_files()

    # Cargar progreso
    global downloaded_files
    downloaded_files = load_progress()

    # Paso 3: Descargar archivos
    print("Paso 3: Descargando archivos. Esto puede tardar un momento...")
    download_thread = Thread(target=scrape_and_download_files, args=(BASE_URL, LOCAL_DIR, downloaded_files, ignore_folders, ignore_files))
    download_thread.start()

    # Iniciar el bucle principal de tkinter
    global root
    root = tk.Tk()
    root.title("Espectrograma en tiempo real")

    # Crear figura para espectrograma
    global ax
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.ion()  # Habilitar modo interactivo
    canvas = fig.canvas
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Iniciar hilo de actualización de la ventana
    update_thread = Thread(target=update_window)
    update_thread.start()

    # Mantener la interfaz gráfica
    root.mainloop()

# Ejecutar el programa
if __name__ == "__main__":
    main()
