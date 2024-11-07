import os
import struct

# Obtener la ruta de la carpeta donde está el archivo del script
folder_path = os.path.dirname(os.path.abspath(__file__))

# Listar todos los archivos en la carpeta que tienen la extensión .bin
bin_files = [f for f in os.listdir(folder_path) if f.endswith('.bin')]

# Procesar cada archivo binario
for bin_file_name in bin_files:
    bin_file_path = os.path.join(folder_path, bin_file_name)

    # Abrir el archivo binario y leer su contenido
    with open(bin_file_path, 'rb') as bin_file:
        bin_data = bin_file.read()

    # Convertir los datos binarios en una lista de enteros de 16 bits
    bin_data_as_ints = struct.unpack('H' * (len(bin_data) // 2), bin_data)

    # Crear el nombre del archivo de salida basado en el archivo binario
    output_file_name = bin_file_name.replace('.bin', '_salida.txt')
    output_file_path = os.path.join(folder_path, output_file_name)

    # Escribir el contenido en el archivo de texto
    with open(output_file_path, 'w') as output_file:
        for num in bin_data_as_ints:
            output_file.write(f'{num}\n')

    print(f"El archivo binario {bin_file_name} se ha guardado en '{output_file_name}'")

print("Todos los archivos binarios han sido procesados.")
