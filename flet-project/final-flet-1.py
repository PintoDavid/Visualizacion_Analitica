import os
import struct
import json
import pandas as pd
import flet as ft
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from io import BytesIO
import math
import base64


class COVISProcessorFlet:
    def __init__(self, page):
        self.page = page

        # Variables para datos
        self.folder_path = None
        self.index_csv = None
        self.bin_files = []
        self.json_files = []
        self.bin_data = []
        self.json_data = []
        self.index_data = None
        self.current_index = 0

        # Interfaz
        self.file_list = ft.ListView(height=200, expand=True)
        self.slider = ft.Slider(min=0, max=1, divisions=1, label="Índice: {value}")
        self.output_chart = ft.Image(expand=True)
        self.json_area = ft.TextField(
            value="", multiline=True, expand=True, read_only=True, border_width=0
        )

        # Inicializar
        self.create_ui()

    def create_ui(self):
        """Crea la interfaz principal de la aplicación."""
        self.page.title = "Procesamiento COVIS"
        self.page.add(
            ft.Row(
                [
                    ft.Column(
                        [
                            ft.ElevatedButton(
                                "Seleccionar Carpeta", on_click=self.select_folder
                            ),
                            ft.Text("Archivos BIN encontrados:"),
                            self.file_list,
                            ft.Text("Control deslizante:"),
                            self.slider,
                        ],
                        width=200,
                    ),
                    ft.Column(
                        [
                            ft.Text("Gráficas:"),
                            self.output_chart,
                        ],
                        expand=True,
                    ),
                    ft.Column(
                        [
                            ft.Text("Contenido del JSON:"),
                            self.json_area,
                        ],
                        width=200,
                    ),
                ]
            )
        )

    def select_folder(self, event):
        """Selecciona la carpeta y procesa los archivos."""
        folder = self.page.get_directory_path(dialog_title="Seleccionar carpeta")
        if folder:
            self.process_folder(folder)

    def process_folder(self, folder):
        """Procesa la carpeta seleccionada."""
        self.folder_path = folder
        files = os.listdir(self.folder_path)

        # Separar archivos por tipo
        self.index_csv = [f for f in files if f.endswith(".csv") and "index" in f]
        self.bin_files = sorted([f for f in files if f.endswith(".bin")])
        self.json_files = sorted([f for f in files if f.endswith(".json")])

        if not self.index_csv:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("No se encontró ningún archivo index.csv."), open=True
            )
            return

        # Cargar los datos
        self.process_index_csv()
        self.process_bin_files()
        self.process_json_files()

        # Actualizar lista de archivos BIN
        self.file_list.controls.clear()
        for i, bin_file in enumerate(self.bin_files):
            self.file_list.controls.append(
                ft.ListTile(
                    title=ft.Text(bin_file),
                    on_click=lambda e, index=i: self.update_visualizations(index),
                )
            )
        self.file_list.update()

        # Configurar slider
        self.slider.max = len(self.bin_files) - 1
        self.slider.divisions = len(self.bin_files) - 1
        self.slider.on_change = self.slider_changed
        self.slider.update()

        # Mostrar la primera visualización
        self.update_visualizations(0)

    def process_index_csv(self):
        """Procesa el archivo index.csv para obtener información clave."""
        index_path = os.path.join(self.folder_path, self.index_csv[0])
        self.index_data = pd.read_csv(index_path)

    def process_bin_files(self):
        """Procesa los archivos BIN y extrae datos."""
        def read_bin_data(bin_path, scale_factor=1e6):
            """Lee y escala los datos de un archivo BIN."""
            bin_data = []
            with open(bin_path, "rb") as f:
                while chunk := f.read(4):  # Leer en bloques de 4 bytes
                    try:
                        value = struct.unpack("<f", chunk)[0]
                        if math.isnan(value) or math.isinf(value):
                            value = 0
                        bin_data.append(value * scale_factor)
                    except struct.error:
                        bin_data.append(0)
            return bin_data

        self.bin_data = [
            read_bin_data(os.path.join(self.folder_path, bin_file))
            for bin_file in self.bin_files
        ]

    def process_json_files(self):
        """Procesa los archivos JSON y extrae metadatos."""
        def process_json_file(json_path):
            """Extrae datos de un archivo JSON."""
            with open(json_path, "r") as f:
                return json.load(f)

        self.json_data = [
            process_json_file(os.path.join(self.folder_path, json_file))
            for json_file in self.json_files
        ]

    def slider_changed(self, event):
        """Actualiza las visualizaciones al mover el slider."""
        self.update_visualizations(int(self.slider.value))

    def update_visualizations(self, index):
        """Actualiza las gráficas y el área JSON."""
        self.current_index = index

        # Datos del CSV y BIN
        row = self.index_data.iloc[index]
        bin_data = self.bin_data[index]
        json_data = self.json_data[index]

        # Crear gráficas
        fig = plt.figure(figsize=(12, 8))

        # Gráfica 1: Polar
        ax1 = fig.add_subplot(221, projection="polar")
        ax1.plot([0, row["kPAngle"]], [0, row["kRAngle"]], marker="o")
        ax1.set_title("Representación Polar")

        # Gráfica 2: 3D Ángulos
        ax2 = fig.add_subplot(222, projection="3d")
        ax2.quiver(0, 0, 0, row["pitch"], row["roll"], row["yaw"], length=0.1, normalize=True)
        ax2.set_title("Representación 3D (Ángulos CSV)")

        # Gráfica 3: BIN (2D)
        ax3 = fig.add_subplot(223)
        ax3.plot(range(len(bin_data)), bin_data, "b-")
        ax3.set_title(f"Archivo BIN: {self.bin_files[index]}")

        # Gráfica 4: BIN (3D)
        ax4 = fig.add_subplot(224, projection="3d")
        bin_x = range(len(bin_data))
        bin_z = [sum(bin_data[:i + 1]) for i in range(len(bin_data))]
        ax4.scatter(bin_x, bin_data, bin_z, c=bin_z, cmap="viridis", marker="o")
        ax4.set_title("Visualización 3D (BIN como puntos)")

        # Convertir la figura en imagen para Flet
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close(fig)

        # Convertir a base64
        self.output_chart.src_base64 = base64.b64encode(buf.read()).decode("utf-8")
        self.output_chart.update()

        # Actualizar área JSON
        self.json_area.value = json.dumps(json_data, indent=4)
        self.json_area.update()


# Ejecutar aplicación Flet
def main(page: ft.Page):
    app = COVISProcessorFlet(page)


ft.app(target=main)
