import json
import numpy as np

def process_files(file_paths):
    results = {}
    for file_path in file_paths:
        if file_path.endswith('.json'):
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Suponiendo que los datos son una lista de objetos con x, y
                processed_data = [{'x': item['x'], 'y': item['y']} for item in data]
                results[file_path] = {'processed_data': processed_data}
        elif file_path.endswith('.bin'):
            data = np.fromfile(file_path, dtype=np.float64)
            processed_data = [{'x': i, 'y': value} for i, value in enumerate(data)]
            results[file_path] = {'processed_data': processed_data}
        else:
            results[file_path] = {'error': 'Tipo de archivo no soportado.'}
    return results
