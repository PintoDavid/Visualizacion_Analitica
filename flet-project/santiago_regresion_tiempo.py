import struct
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import json


# Nombres de los archivos
binary_file_name = 'rec_7038_000005.bin'
json_file_name = 'rec_7000_001030.json'

# Función para leer el archivo JSON
def read_json_config(json_path):
    with open(json_path, 'r') as json_file:
        config = json.load(json_file)
    return config

# Función para leer el archivo binario
def read_sonar_data(binary_path):
    with open(binary_path, 'rb') as file:
        data = file.read()
        num_entries = len(data) // 16
        sonar_data = []
        for i in range(num_entries):
            entry = struct.unpack('<4f', data[i*16:(i+1)*16])
            sonar_data.append(entry)
        return sonar_data

# Leer la configuración del JSON
config = read_json_config(json_file_name)

# Leer los datos del sonar
sonar_data = read_sonar_data(binary_file_name)

# Extraer valores para graficar
filtered_times = []
filtered_amplitudes = []
for entry in sonar_data:
    time = entry[1]  # Ajusta el índice según tu estructura
    amplitude = entry[0]  # Ajusta el índice según tu estructura

    if time >= 0 and amplitude >= -40:
        filtered_times.append(time)
        filtered_amplitudes.append(amplitude)

# Crear la figura y los ejes
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.1, bottom=0.25)

# Graficar la primera toma por defecto
point, = plt.plot(filtered_times[0], filtered_amplitudes[0], 'bo')
plt.xlim(min(filtered_times), max(filtered_times))
plt.ylim(min(filtered_amplitudes), max(filtered_amplitudes))
plt.xlabel('Tiempo (segundos)')
plt.ylabel('Amplitud (dB)')
plt.title(f'Toma del sensor en el tiempo: {filtered_times[0]} s')
plt.grid()

# Crear el slider
ax_slider = plt.axes([0.1, 0.1, 0.8, 0.03], facecolor='lightgoldenrodyellow')
slider = Slider(ax_slider, 'Índice', 0, len(filtered_times) - 1, valinit=0, valfmt='%d')

# Función para actualizar la gráfica con el slider
def update(val):
    index = int(slider.val)
    point.set_data([filtered_times[index]], [filtered_amplitudes[index]])
    ax.set_title(f'Toma del sensor en el tiempo: {filtered_times[index]} s')
    fig.canvas.draw_idle()

# Conectar el slider con la función de actualización
slider.on_changed(update)

plt.show()