import os

def listar_archivos_en_ruta(ruta_archivo):
    ruta_directorio = os.path.dirname(ruta_archivo)
    archivos = [f for f in os.listdir(ruta_directorio) if os.path.isfile(os.path.join(ruta_directorio, f))]
    return archivos

def leer_archivo_ascii(ruta_archivo, metodo):
    try:
        with open(ruta_archivo, 'r', encoding='ascii') as archivo:
            if metodo == '1':
                print("Leyendo archivo línea por línea:")
                for linea in archivo:
                    print(linea.strip())
            elif metodo == '2':
                print("Leyendo todo el archivo de una vez:")
                contenido = archivo.read()
                print(contenido)
            elif metodo == '3':
                print("Leyendo archivo como lista de líneas:")
                contenido = archivo.readlines()
                for linea in contenido:
                    print(linea.strip())
            else:
                print("Método no válido.")
    except FileNotFoundError:
        print(f"El archivo {ruta_archivo} no se encontró.")
    except UnicodeDecodeError:
        print(f"El archivo {ruta_archivo} no está en formato ASCII.")
    except Exception as e:
        print(f"Ha ocurrido un error: {e}")

def seleccionar_archivo_y_leer():
    # Usa 'copy path' para obtener la ruta del archivo y dará la lista de archivos a leer
    ruta_archivo = input("Introduce la ruta de cualquier archivo en la carpeta que deseas explorar: ")
    archivos = listar_archivos_en_ruta(ruta_archivo)

    if not archivos:
        print("No se encontraron archivos en la carpeta especificada.")
        return

    print("Archivos disponibles:")
    for i, archivo in enumerate(archivos):
        print(f"{i + 1}: {archivo}")

    seleccion = int(input("Selecciona el número del archivo que quieres leer: ")) - 1

    if seleccion < 0 or seleccion >= len(archivos):
        print("Selección no válida.")
        return

    archivo_seleccionado = os.path.join(os.path.dirname(ruta_archivo), archivos[seleccion])

    print("Selecciona el método para leer el archivo:")
    print("1: Línea por línea")
    print("2: Todo el archivo de una vez")
    print("3: Como una lista de líneas")
    metodo = input("Introduce el número del método: ")

    leer_archivo_ascii(archivo_seleccionado, metodo)

# Ejecutar el programa
seleccionar_archivo_y_leer()
