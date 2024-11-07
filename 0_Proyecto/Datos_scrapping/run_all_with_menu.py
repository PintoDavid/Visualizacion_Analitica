import subprocess

# Función para ejecutar un script
def run_script(script_name):
    print(f"Ejecutando: {script_name}...")
    try:
        subprocess.run(['python', script_name], check=True)
        print(f"Completado: {script_name}\n")
    except subprocess.CalledProcessError as e:
        print(f"Ocurrió un error al ejecutar {script_name}: {e}\n")

# Función para mostrar el menú y obtener la opción del usuario
def show_menu():
    print("Seleccione una opción para ejecutar:")
    print("1. Descargar datos")
    print("2. Procesar datos")
    print("3. Mostrar datos")
    print("4. Salir")

# Función principal
def main():
    scripts = {
        "1": "download_data.py",
        "2": "process_data.py",
        "3": "display_data.py"
    }

    executed_scripts = set()  # Para llevar un registro de los scripts ejecutados

    while True:
        show_menu()
        choice = input("Ingrese su opción (1-4): ")

        if choice in scripts:
            script_name = scripts[choice]
            if script_name in executed_scripts:
                print(f"{script_name} ya ha sido ejecutado. Elija otro script.\n")
            else:
                run_script(script_name)
                executed_scripts.add(script_name)  # Marcar como ejecutado
        elif choice == "4":
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Intente de nuevo.\n")

if __name__ == "__main__":
    main()
