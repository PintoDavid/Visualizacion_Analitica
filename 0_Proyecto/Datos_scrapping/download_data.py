import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# URL base
BASE_URL = "http://piweb.ooirsn.uw.edu/covis/data/BROWSE/2023/"

# Archivo para almacenar el progreso
PROGRESS_FILE = "download_progress.resume"

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

# Verificar si un archivo ya está completo
def is_file_complete(output_path, file_size):
    if os.path.exists(output_path):
        local_size = os.path.getsize(output_path)
        return local_size == file_size  # Comparar el tamaño local con el tamaño en el servidor
    return False

# Descargar archivos uno por uno directamente
def download_file(url, output_path, downloaded_files):
    try:
        # Verificar si el archivo ya está descargado
        head_response = requests.head(url)
        file_size = int(head_response.headers.get('content-length', 0))  # Obtener el tamaño

        if is_file_complete(output_path, file_size):
            print(f"Ya descargado: {output_path}")
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
        downloaded_files.add(output_path)  # Añadir al progreso
        save_progress(downloaded_files)  # Guardar progreso

    except Exception as e:
        print(f"Error al descargar {output_path}: {e}")

# Scraping dinámico para descargar archivos directamente
def scrape_and_download_files(base_url, current_dir, downloaded_files):
    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Verificar si la solicitud fue exitosa
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')

        # Recorrer los enlaces para buscar archivos
        for link in links:
            href = link.get('href')
            if href.endswith('/'):  # Si es un directorio
                new_dir = os.path.join(current_dir, href)
                # Llamar recursivamente para explorar la subcarpeta
                scrape_and_download_files(base_url + href, new_dir, downloaded_files)
            elif href.endswith('.tar.gz'):  # Si es un archivo .tar.gz
                file_url = base_url + href
                output_path = os.path.join(current_dir, href)
                download_file(file_url, output_path, downloaded_files)  # Descargar inmediatamente

    except Exception as e:
        print(f"No se pudo conectar a: {base_url} - Error: {e}")

# Definir el directorio base local para almacenar los archivos
LOCAL_DIR = "covis_data_cloned"

# Cargar el progreso anterior
downloaded_files = load_progress()

# Llamar a la función de scraping y descarga directa
scrape_and_download_files(BASE_URL, LOCAL_DIR, downloaded_files)
