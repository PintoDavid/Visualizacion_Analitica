import requests
import os

# URL del servidor de datos
data_url = "http://piweb.ooirsn.uw.edu/covis/data/some_data_file.tar.gz"
save_path = "./data/some_data_file.tar.gz"

# Crear el directorio si no existe
if not os.path.exists(os.path.dirname(save_path)):
    os.makedirs(os.path.dirname(save_path))

# Descargar el archivo
response = requests.get(data_url, stream=True)
if response.status_code == 200:
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Descarga completada: {save_path}")
else:
    print(f"Error al descargar los datos: {response.status_code}")