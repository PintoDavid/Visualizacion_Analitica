import requests
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_file(file_url, file_path):
    print(f'Descargando archivo: {file_url}')
    response = requests.get(file_url)
    with open(file_path, 'wb') as file:
        file.write(response.content)

def download_files_from_url(url, base_path):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    os.makedirs(base_path, exist_ok=True)
    
    futures = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and not href.startswith('..'):
                file_url = url + href
                if not href.endswith('/'):
                    # Descargar archivo en paralelo
                    file_path = os.path.join(base_path, href)
                    futures.append(executor.submit(download_file, file_url, file_path))
                else:
                    # Llamar recursivamente para directorios
                    print(f'Entrando en directorio: {file_url}')
                    download_files_from_url(file_url, os.path.join(base_path, href))

        # Esperar a que todas las descargas se completen
        for future in as_completed(futures):
            future.result()  # Esto también puede capturar excepciones si ocurren

# URL de la carpeta
url = "http://piweb.ooirsn.uw.edu/covis/data/BROWSE/2023/"
download_files_from_url(url, 'COVIS-2023')

print("Descarga completa.")