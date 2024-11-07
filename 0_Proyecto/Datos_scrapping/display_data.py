import os
import json
import pandas as pd
import tkinter as tk
from tkinter import ttk

# Directorio donde se descargaron y descomprimieron los archivos
DOWNLOAD_DIR = "covis_data_cloned"  # El mismo directorio donde se descomprimieron los archivos en el script 2

# Función para leer archivos JSON y convertirlos a DataFrame de pandas
def load_json_files(directory):
    dataframes = []
    
    # Recorrer todos los subdirectorios en busca de archivos JSON
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as json_file:
                        data = json.load(json_file)
                        # Convertir a DataFrame, cada JSON debe ser una lista de registros o un diccionario
                        df = pd.DataFrame(data)
                        dataframes.append(df)
                except Exception as e:
                    print(f"Error al leer {file_path}: {e}")
    
    # Combinar todos los DataFrames en uno solo
    if dataframes:
        return pd.concat(dataframes, ignore_index=True)
    else:
        print("No se encontraron archivos JSON.")
        return pd.DataFrame()  # Retornar DataFrame vacío si no hay datos

# Función para mostrar los datos en una ventana
def display_dataframe(df):
    if df.empty:
        print("No hay datos para mostrar.")
        return
    
    # Crear la ventana principal
    root = tk.Tk()
    root.title("Datos JSON en Tabla")

    # Crear un marco (frame) para la tabla
    frame = ttk.Frame(root)
    frame.pack(fill="both", expand=True)

    # Crear un Treeview (tabla)
    tree = ttk.Treeview(frame, columns=list(df.columns), show="headings")

    # Definir los encabezados de las columnas
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    # Insertar los datos fila por fila
    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    # Colocar la tabla en la ventana
    tree.pack(fill="both", expand=True)

    # Agregar un botón para cerrar la ventana
    button = ttk.Button(root, text="Cerrar", command=root.destroy)
    button.pack()

    # Iniciar el bucle principal de tkinter
    root.mainloop()

# Main script
if __name__ == "__main__":
    # Directorio de descarga y descompresión definido en el script
    directory = DOWNLOAD_DIR

    if directory and os.path.exists(directory):
        # Cargar y mostrar los datos
        print(f"Leyendo archivos JSON de: {directory}")
        df = load_json_files(directory)

        if not df.empty:
            print(f"Mostrando {len(df)} filas de datos.")
            display_dataframe(df)
        else:
            print("No se encontraron datos válidos.")
    else:
        print(f"El directorio {directory} no existe. Asegúrate de que el script 2 se haya ejecutado correctamente.")
