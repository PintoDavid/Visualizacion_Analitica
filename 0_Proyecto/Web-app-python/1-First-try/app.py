from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
import numpy as np
import json
import random

app = Flask(__name__)

# Ruta para servir la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar la selección de archivos y procesarlos
@app.route('/process-files', methods=['POST'])
def process_files():
    folder_path = request.form['folderPath']
    folder_path = os.path.abspath(folder_path)  # Convertir a ruta absoluta
    if not os.path.exists(folder_path):
        return "Error: Carpeta no encontrada", 400
    
    data_files = [f for f in os.listdir(folder_path) if f.endswith(('.json', '.bin'))]
    
    # Cargar y procesar archivos JSON y BIN
    processed_data = []
    for file_name in data_files:
        file_path = os.path.join(folder_path, file_name)
        
        if file_name.endswith('.json'):
            with open(file_path, 'r') as f:
                data = json.load(f)
            # Procesar los datos JSON (Ejemplo simple)
            data_array = np.array(data['values'])
        
        elif file_name.endswith('.bin'):
            data = np.fromfile(file_path, dtype=np.float32)
            data_array = data.reshape(-1, 3)
        
        # Aplicar cálculos (ejemplo)
        processed_result = {
            'file': file_name,
            'data': data_array.tolist(),
            'calculation_result': random.choice(data_array).tolist()  # Ejemplo de resultado de cálculo
        }
        processed_data.append(processed_result)
    
    return jsonify(processed_data)

if __name__ == '__main__':
    app.run(debug=True)
