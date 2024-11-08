from flask import Flask, request, jsonify, render_template, url_for, redirect
import os
from werkzeug.utils import secure_filename
from app.file_processing import process_files

app = Flask(__name__)

UPLOAD_FOLDER = 'uploaded_files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

processed_data = None  # Almacena los datos procesados para usarlos en la visualización

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload-folder', methods=['POST'])
def upload_folder():
    global processed_data  # Usar una variable global para mantener datos procesados en sesión
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    uploaded_files = request.files.getlist('files')
    saved_files = []

    for file in uploaded_files:
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        saved_files.append(save_path)

    # Procesar archivos
    processed_data = process_files(saved_files)
    return jsonify({'message': 'Archivos procesados correctamente'})

@app.route('/visualize')
def visualize():
    if processed_data:
        return render_template('visualize.html', data=processed_data)
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
