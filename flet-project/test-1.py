import os
import struct
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from mpl_toolkits.mplot3d import Axes3D
from tkinter import Tk, filedialog
import math


class COVISProcessor:
    def __init__(self):
        # Variables para datos
        self.folder_path = None
        self.index_csv = None
        self.bin_files = []
        self.json_files = []
        self.bin_data = []
        self.json_data = []
        self.index_data = None

        # Configurar la ventana principal
        self.root = Tk()
        self.root.title("Procesamiento COVIS")
        self.root.withdraw()  # Ocultar ventana principal de Tkinter

        # Iniciar el proceso
        self.run()

    def run(self):
        """Ejecuta todo el flujo automáticamente."""
        self.select_folder()
        if not self.folder_path:
            print("No se seleccionó ninguna carpeta. Finalizando.")
            return

        print("Procesando archivos...")
        self.process_index_csv()
        self.process_bin_files()
        self.process_json_files()
        print("Archivos procesados. Iniciando visualización...")
        self.setup_visualization()

    def select_folder(self):
        """Selecciona la carpeta con los archivos necesarios."""
        self.folder_path = filedialog.askdirectory(title="Seleccionar carpeta con archivos COVIS")
        if not self.folder_path:
            return
        
        files = os.listdir(self.folder_path)

        # Separar archivos por tipo
        self.index_csv = [f for f in files if f.endswith('.csv') and 'index' in f]
        self.bin_files = sorted([f for f in files if f.endswith('.bin')])
        self.json_files = sorted([f for f in files if f.endswith('.json')])

        if not self.index_csv:
            print("Error: No se encontró ningún archivo index.csv en la carpeta seleccionada.")
            self.folder_path = None

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
                        value = struct.unpack('<f', chunk)[0]
                        # Reemplazar valores NaN o Inf por 0
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
            with open(json_path, 'r') as f:
                return json.load(f)
        
        self.json_data = [
            process_json_file(os.path.join(self.folder_path, json_file))
            for json_file in self.json_files
        ]

    def setup_visualization(self):
        """Configura las visualizaciones."""
        # Configurar las gráficas
        fig = plt.figure(figsize=(14, 12))
        ax1 = fig.add_subplot(231, projection="polar")  # Gráfica polar
        ax2 = fig.add_subplot(232, projection="3d")     # Gráfica 3D (ángulos CSV)
        ax3 = fig.add_subplot(233)                      # Gráfica BIN
        ax4 = fig.add_subplot(234, frame_on=False)      # Texto JSON
        ax4.axis("off")
        ax5 = fig.add_subplot(235, projection="3d")     # Gráfica 3D combinada

        # Crear slider
        slider_ax = plt.axes([0.2, 0.02, 0.65, 0.03], facecolor="lightgoldenrodyellow")
        slider = Slider(slider_ax, "Fila/BIN", 0, len(self.bin_files) - 1, valinit=0, valfmt="%0.0f")

        def update(val):
            index = int(slider.val)

            # Gráfica 1: Representación 2D (polar)
            row = self.index_data.iloc[index]
            kPAngle = row["kPAngle"]
            kRAngle = row["kRAngle"]
            ax1.clear()
            ax1.plot([0, kPAngle], [0, kRAngle], marker="o")
            ax1.set_title("Representación Polar")

            # Gráfica 2: Representación 3D (ángulos CSV)
            pitch, roll, yaw = row["pitch"], row["roll"], row["yaw"]
            ax2.clear()
            ax2.quiver(0, 0, 0, pitch, roll, yaw, length=0.1, normalize=True)
            ax2.set_title("Representación 3D (Ángulos CSV)")

            # Gráfica 3: Datos BIN
            bin_data = self.bin_data[index]
            ax3.clear()
            ax3.plot(range(len(bin_data)), bin_data, "b-")
            ax3.set_title(f"Archivo BIN: {self.bin_files[index]}")
            ax3.set_xlabel("Índice")
            ax3.set_ylabel("Valor")

            # Cuadro de texto para JSON
            ax4.clear()
            ax4.text(0, 1, json.dumps(self.json_data[index], indent=4), fontsize=8, ha="left", va="top", wrap=True)
            ax4.set_title("Contenido JSON")

            # Gráfica 4: Representación combinada 3D
            ax5.clear()
            json_hdr = self.json_data[index]["hdr"]
            origin_x = json_hdr.get("horiz_angle", 0)
            origin_y = json_hdr.get("vert_angle", 0)
            origin_z = 0  # Origen en Z
            
            trajectory_x = [origin_x + i * pitch for i in range(len(bin_data))]
            trajectory_y = [origin_y + i * roll for i in range(len(bin_data))]
            trajectory_z = bin_data
            
            # Origen y vectores
            ax5.scatter(origin_x, origin_y, origin_z, color="red", label="Origen (JSON)", s=50)
            ax5.quiver(origin_x, origin_y, origin_z, pitch, roll, yaw, length=0.1, color="green", label="Ángulos (CSV)")
            ax5.plot(trajectory_x, trajectory_y, trajectory_z, color="blue", label="Trayectoria (BIN)")
            ax5.set_title("Visualización combinada 3D")
            ax5.set_xlabel("X (kPAngle)")
            ax5.set_ylabel("Y (kRAngle)")
            ax5.set_zlabel("Z (Trayectoria BIN)")
            ax5.legend()

            fig.canvas.draw_idle()

        slider.on_changed(update)
        update(0)
        plt.show()


# Iniciar el procesamiento automáticamente
COVISProcessor()
