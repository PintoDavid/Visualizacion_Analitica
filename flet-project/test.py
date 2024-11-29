import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.impute import SimpleImputer

class DataVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Visualizer")

        # Variables de control
        self.json_data = []
        self.bin_data = []
        self.current_file_index = tk.IntVar(value=0)  # Usar IntVar para manejar el índice
        self.selected_json_key = tk.StringVar()
        self.num_clusters = tk.IntVar(value=3)
        self.num_iterations = tk.IntVar(value=100)
        self.show_silhouette = tk.BooleanVar(value=True)
        self.show_violin = tk.BooleanVar(value=True)
        self.swap_axes = tk.BooleanVar(value=False)
        self.filter_clusters = tk.BooleanVar(value=False)
        self.selected_cluster = tk.IntVar(value=0)
        self.reduce_data = tk.BooleanVar(value=False)
        self.reduction_percentage = tk.DoubleVar(value=10.0)

        # Crear la interfaz de usuario
        self.create_ui()

    def create_ui(self):
        # Ventana de control
        control_window = tk.Toplevel(self.root)
        control_window.title("Controles UX")

        # Botón para cargar datos
        ttk.Button(control_window, text="Cargar Carpeta", command=self.load_files).pack(pady=5)

        # Dropdown para seleccionar datos JSON
        ttk.Label(control_window, text="Eje Y (Datos JSON)").pack()
        self.json_dropdown = ttk.Combobox(control_window, textvariable=self.selected_json_key)
        self.json_dropdown.pack(pady=5)

        # Check para intercambiar ejes
        ttk.Checkbutton(control_window, text="Intercambiar Ejes", variable=self.swap_axes, command=self.update_graph).pack(pady=5)

        # Check para mostrar/ocultar coeficiente silueta
        ttk.Checkbutton(control_window, text="Mostrar Coeficiente Silueta", variable=self.show_silhouette, command=self.update_graph).pack(pady=5)

        # Check para mostrar/ocultar gráfico de violín
        ttk.Checkbutton(control_window, text="Mostrar Gráfico de Violín", variable=self.show_violin, command=self.update_graph).pack(pady=5)

        # Slider para número de clusters
        ttk.Label(control_window, text="Número de Clusters").pack()
        ttk.Scale(control_window, from_=2, to_=10, variable=self.num_clusters, orient=tk.HORIZONTAL, command=lambda _: self.update_graph()).pack(pady=5)

        # Slider para número de iteraciones
        ttk.Label(control_window, text="Número de Iteraciones").pack()
        ttk.Scale(control_window, from_=10, to_=500, variable=self.num_iterations, orient=tk.HORIZONTAL, command=lambda _: self.update_graph()).pack(pady=5)

        # Check para filtrar clusters
        ttk.Checkbutton(control_window, text="Filtrar Clusters", variable=self.filter_clusters, command=self.update_graph).pack(pady=5)

        # Slider para seleccionar cluster
        ttk.Label(control_window, text="Cluster Seleccionado").pack()
        self.cluster_slider = ttk.Scale(control_window, from_=0, to_=10, variable=self.selected_cluster, orient=tk.HORIZONTAL, command=lambda _: self.update_graph())
        self.cluster_slider.pack(pady=5)
        self.cluster_slider.state(["disabled"])

        # Check para habilitar reducción de datos
        ttk.Checkbutton(control_window, text="Habilitar Reducción de Datos", variable=self.reduce_data, command=self.update_reduction_slider).pack(pady=5)

        # Slider para porcentaje de reducción
        ttk.Label(control_window, text="Porcentaje de Reducción").pack()
        self.reduction_slider = ttk.Scale(control_window, from_=0, to_=100, variable=self.reduction_percentage, orient=tk.HORIZONTAL, command=lambda _: self.update_graph())
        self.reduction_slider.pack(pady=5)
        self.reduction_slider.state(["disabled"])

        # Slider para cambiar entre los archivos
        ttk.Label(control_window, text="Cambiar Archivos").pack()
        self.file_slider = ttk.Scale(control_window, from_=0, to_=10, variable=self.current_file_index, orient=tk.HORIZONTAL, command=lambda _: self.update_graph())
        self.file_slider.pack(pady=5)
        self.file_slider.state(["disabled"])

        # Canvas para las gráficas
        self.figure, (self.ax_main, self.ax_silhouette, self.ax_violin) = plt.subplots(1, 3, figsize=(15, 5))
        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_files(self):
        folder = filedialog.askdirectory(title="Seleccionar Carpeta")
        if not folder:
            return

        # Cargar archivos BIN y JSON en la carpeta
        self.bin_files = [f for f in os.listdir(folder) if f.endswith('.bin')]
        self.json_files = [f for f in os.listdir(folder) if f.endswith('.json')]

        if len(self.bin_files) != len(self.json_files):
            messagebox.showerror("Error", "El número de archivos .bin y .json no coincide.")
            return

        # Leer archivos
        self.bin_data = []
        self.json_data = []

        for bin_file, json_file in zip(self.bin_files, self.json_files):
            try:
                with open(os.path.join(folder, bin_file), "rb") as f:
                    self.bin_data.append(np.frombuffer(f.read(), dtype=np.float32))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo BIN: {e}")
                return

            try:
                with open(os.path.join(folder, json_file), "r") as f:
                    self.json_data.append(json.load(f))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo JSON: {e}")
                return

        # Activar el slider para cambiar entre archivos
        if len(self.bin_files) > 1:
            self.file_slider.config(to=len(self.bin_files) - 1)
            self.file_slider.state(["!disabled"])

        # Actualizar el título de la ventana con el primer archivo
        self.update_file()

    def update_file(self):
        # Verificar que el índice esté dentro del rango
        if 0 <= self.current_file_index.get() < len(self.bin_data):
            bin_data = self.bin_data[self.current_file_index.get()]
            json_data = self.json_data[self.current_file_index.get()]

            # Actualizar el dropdown con las claves JSON
            self.json_dropdown["values"] = list(json_data.keys())
            if json_data.keys():
                self.selected_json_key.set(list(json_data.keys())[0])

            # Actualizar el título de la ventana
            self.root.title(f"Visualizando: {self.json_files[self.current_file_index.get()]} vs {self.bin_files[self.current_file_index.get()]}")

            # Graficar
            self.update_graph()
        else:
            messagebox.showerror("Error", "Índice de archivo fuera de rango.")

    def update_graph(self):
        self.ax_main.clear()
        self.ax_silhouette.clear()
        self.ax_violin.clear()

        if not self.bin_data or not self.selected_json_key.get():
            return

        # Obtener datos para graficar
        bin_data = self.bin_data[self.current_file_index.get()]
        json_data = np.array(self.json_data[self.current_file_index.get()][self.selected_json_key.get()])

        # Comprobar si hay valores NaN en los datos
        if np.any(np.isnan(bin_data)) or np.any(np.isnan(json_data)):
            messagebox.showerror("Error", "Los datos contienen valores NaN. No se puede realizar KMeans.")
            return

        # Intercambio de ejes
        if self.swap_axes.get():
            x_data, y_data = json_data, bin_data
        else:
            x_data, y_data = bin_data, json_data

        # Reducción de datos
        if self.reduce_data.get():
            reduction_factor = int(len(x_data) * (self.reduction_percentage.get() / 100))
            indices = np.random.choice(len(x_data), len(x_data) - reduction_factor, replace=False)
            x_data = x_data[indices]
            y_data = y_data[indices]

        # KMeans y Silhouette
        kmeans = KMeans(n_clusters=self.num_clusters.get(), max_iter=self.num_iterations.get())
        clusters = kmeans.fit_predict(x_data.reshape(-1, 1))

        silhouette_avg = silhouette_score(x_data.reshape(-1, 1), clusters)

        # Graficar en el primer gráfico
        self.ax_main.scatter(x_data, y_data, c=clusters, cmap="viridis")
        self.ax_main.set_title(f"Gráfico de Datos: KMeans (Silhouette: {silhouette_avg:.2f})")

        # Graficar coeficiente silueta
        if self.show_silhouette.get():
            self.ax_silhouette.bar(range(len(clusters)), silhouette_avg)
            self.ax_silhouette.set_title("Coeficiente de Silueta")

        # Graficar violín
        if self.show_violin.get():
            sns.violinplot(x=clusters, y=x_data, ax=self.ax_violin)

        # Actualizar la gráfica
        self.canvas.draw()

    def update_reduction_slider(self):
        if self.reduce_data.get():
            self.reduction_slider.state(["!disabled"])
        else:
            self.reduction_slider.state(["disabled"])
