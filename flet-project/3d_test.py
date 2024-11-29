import numpy as np
import pandas as pd
import pyvista as pv
from tkinter import Tk, filedialog
import struct
import json

# ---------------------------
# Funciones de lectura
# ---------------------------

def read_index_csv(file_path):
    """Lee el archivo index.csv y devuelve un DataFrame."""
    return pd.read_csv(file_path)


def read_bin_data(bin_path):
    """Lee datos binarios del archivo BIN y devuelve un array."""
    bin_data = []
    with open(bin_path, "rb") as f:
        while chunk := f.read(4):  # Leer 4 bytes por dato
            try:
                value = struct.unpack('<f', chunk)[0]
                if np.isnan(value) or np.isinf(value):
                    value = 0  # Reemplazar NaN o inf por 0
                bin_data.append(value)
            except struct.error:
                continue
    return np.array(bin_data)


def read_json_file(json_path):
    """Lee el archivo JSON y devuelve un diccionario."""
    with open(json_path, "r") as f:
        return json.load(f)


# ---------------------------
# Procesamiento de datos
# ---------------------------

def generate_plume_points(index_data, bin_data, json_data):
    """
    Genera una nube de puntos 3D para representar la pluma hidrotermal.
    Usa los datos del archivo BIN como magnitud y del CSV/JSON para las coordenadas.
    """
    points = []
    scalar_values = []

    # Parámetros iniciales de configuración
    x_base, y_base, z_base = 0, 0, 0  # Punto de origen (ajustable)
    step = 10  # Escala espacial entre puntos

    for idx, (row, bin_value) in enumerate(zip(index_data.iterrows(), bin_data)):
        _, row = row
        # Extraer coordenadas simuladas (basadas en ángulos del CSV)
        pitch, roll, yaw = row["pitch"], row["roll"], row["yaw"]
        x = x_base + idx * step
        y = y_base + bin_value * np.cos(np.radians(pitch))
        z = z_base + bin_value * np.sin(np.radians(roll))

        # Añadir punto y magnitud escalar
        points.append([x, y, z])
        scalar_values.append(bin_value)

    return np.array(points), np.array(scalar_values)


def visualize_plume(points, scalars):
    """
    Visualiza la pluma hidrotermal como una nube de puntos volumétrica.
    """
    # Verificar si hay datos válidos
    if len(points) == 0 or len(scalars) == 0:
        print("No se generaron puntos para visualizar.")
        return

    # Crear una nube de puntos
    point_cloud = pv.PolyData(points)
    point_cloud["Scalars"] = scalars

    # Visualización inicial de los puntos
    plotter = pv.Plotter()
    plotter.add_mesh(
        point_cloud,
        scalars="Scalars",
        point_size=10,
        render_points_as_spheres=True,
        cmap="coolwarm",
        show_scalar_bar=True,
    )
    plotter.add_axes()
    plotter.show_grid()
    plotter.show(title="Visualización inicial de Puntos 3D")

    # Crear una interpolación volumétrica (malla de datos)
    grid = point_cloud.delaunay_3d()
    plotter = pv.Plotter()
    plotter.add_mesh(
        grid,
        scalars="Scalars",
        opacity="linear",
        cmap="coolwarm",
        show_scalar_bar=True,
    )
    plotter.add_axes()
    plotter.show_grid()
    plotter.show(title="Visualización Volumétrica 3D")


# ---------------------------
# Programa principal
# ---------------------------

def main():
    root = Tk()
    root.withdraw()

    # Seleccionar carpeta
    folder_path = filedialog.askdirectory(title="Seleccionar carpeta con datos")
    if not folder_path:
        print("No se seleccionó ninguna carpeta.")
        return

    try:
        # Detectar y cargar datos
        index_csv_path = filedialog.askopenfilename(title="Seleccionar archivo index.csv", filetypes=[("CSV Files", "*.csv")])
        bin_path = filedialog.askopenfilename(title="Seleccionar archivo BIN", filetypes=[("BIN Files", "*.bin")])
        json_path = filedialog.askopenfilename(title="Seleccionar archivo JSON", filetypes=[("JSON Files", "*.json")])

        index_data = read_index_csv(index_csv_path)
        bin_data = read_bin_data(bin_path)
        json_data = read_json_file(json_path)

        # Generar puntos y visualizar
        points, scalars = generate_plume_points(index_data, bin_data, json_data)
        visualize_plume(points, scalars)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
