import os
import tarfile
import pandas as pd
import json

# Directorio donde se descargaron los archivos
LOCAL_DIR = "covis_data_cloned"

# Función para descomprimir archivos tar.gz
def extract_files():
    for root, dirs, files in os.walk(LOCAL_DIR):
        for file in files:
            if file.endswith('.tar.gz'):
                file_path = os.path.join(root, file)
                extract_dir = os.path.join(root, file.replace('.tar.gz', ''))
                os.makedirs(extract_dir, exist_ok=True)

                with tarfile.open(file_path, 'r:gz') as tar:
                    tar.extractall(path=extract_dir)
                print(f"Extraído: {file_path} en {extract_dir}")

# Función para leer datos de los archivos extraídos
def read_data():
    all_dataframes = []
    
    for root, dirs, files in os.walk(LOCAL_DIR):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                df = pd.read_csv(file_path)
                all_dataframes.append(df)
                print(f"Leído CSV: {file_path}")
            elif file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as json_file:
                    data = json.load(json_file)
                    df = pd.json_normalize(data)
                    all_dataframes.append(df)
                    print(f"Leído JSON: {file_path}")

    return all_dataframes

if __name__ == "__main__":
    extract_files()
    dataframes = read_data()
    
    # Guardar los DataFrames para usarlos en display_data.py
    pd.to_pickle("dataframes.pkl", dataframes)  # Guardar en un archivo pickle
