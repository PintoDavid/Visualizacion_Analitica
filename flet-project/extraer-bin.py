import struct

# Función para leer el archivo BIN y convertir los datos
def read_bin_data(bin_path):
    bin_data = []
    try:
        with open(bin_path, "rb") as f:
            while chunk := f.read(4):  # Leer en bloques de 4 bytes
                try:
                    value = struct.unpack('<f', chunk)[0]  # Convertir a float (little-endian)
                    bin_data.append(value)
                except struct.error:
                    continue  # Ignorar datos no válidos
    except Exception as e:
        print(f"Error al leer el archivo BIN {bin_path}: {e}")
    return bin_data

# Ruta del archivo BIN
bin_path = "rec_7038_000005.bin"  # Sustituye esto con la ruta de tu archivo

# Leer los datos del archivo BIN
bin_data = read_bin_data(bin_path)

# Mostrar los datos extraídos
print(bin_data)
