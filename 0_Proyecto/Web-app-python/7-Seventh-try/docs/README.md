# Clustering Web App

Esta es una aplicación web para la visualización y análisis de clustering utilizando K-means. La aplicación permite cargar archivos JSON y BIN, procesarlos, y visualizar los resultados de clustering en tiempo real con gráficos interactivos.

## Características

- **Carga de archivos JSON y BIN.**
- **Procesamiento en tiempo real con K-means clustering.**
- **Visualización interactiva con gráficos.**
- **Indicador de progreso durante la carga y el procesamiento.**

## Requisitos

Antes de ejecutar la aplicación, asegúrate de tener instalados los siguientes componentes:

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Dependencias

La aplicación requiere las siguientes librerías de Python:

- Flask
- pandas
- numpy
- scikit-learn

## Instalación

1. Clona este repositorio en tu máquina local.

2. Crea un entorno virtual (opcional pero recomendado):

```python -m venv env
source env/bin/activate  # En Linux/Mac
env\Scripts\activate     # En Windows
```
3. Instala las dependencias necesarias:
```
pip install -r requirements.txt
```
## Ejecución
- Asegúrate de que estás en la carpeta del proyecto.

- Ejecuta la aplicación con el siguiente comando:

```bash
python -m app.main
```
- Abre tu navegador y navega a la siguiente URL:

http://localhost:5000

## Uso
**Cargar archivos:**
En la página principal, selecciona múltiples archivos JSON o BIN para subirlos.

**Visualización de progreso:**
Una barra de progreso mostrará el estado de la carga y el procesamiento.

### Análisis de clustering:

La aplicación procesa los datos y realiza un clustering con K-means.
Los resultados se visualizan de manera interactiva.
Estructura del Proyecto
```csharp
clustering-web-app/
│
├── app/
│   ├── main.py                 # Punto de entrada de la aplicación
│   ├── clustering.py           # Lógica de clustering
│   ├── file_processing.py      # Procesamiento de archivos JSON y BIN
│   ├── templates/
│   │   └── index.html          # Página principal
│   ├── static/
│       ├── styles.css          # Estilos de la página
│       └── progress.js         # Lógica de la barra de progreso
│
├── data/
│   └── input/                  # Carpeta de carga de archivos
│
├── requirements.txt            # Dependencias del proyecto
└── README.md                   # Documentación
```
## Notas
Asegúrate de que los archivos a cargar sean del tipo JSON o BIN
El servidor se ejecuta en modo de desarrollo.
No uses esto en producción sin configuraciones adicionales de seguridad.
## Contribución
Si deseas contribuir al proyecto, sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una nueva rama (git checkout -b feature/nueva-funcionalidad).
3. Realiza tus cambios y haz commit (git commit -m 'Agrega nueva funcionalidad').
4. Haz push a la rama (git push origin feature/nueva-funcionalidad).
5. Abre un Pull Request.
## Licencia
Este proyecto está licenciado bajo la MIT License.