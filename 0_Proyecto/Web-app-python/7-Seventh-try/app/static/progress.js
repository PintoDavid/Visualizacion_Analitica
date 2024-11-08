document.getElementById('folder-form').addEventListener('submit', function (event) {
    event.preventDefault();
    
    const formData = new FormData(this);
    const xhr = new XMLHttpRequest();
    
    xhr.open('POST', '/upload-folder', true);

    xhr.upload.onprogress = function (e) {
        if (e.lengthComputable) {
            const percentComplete = Math.round((e.loaded / e.total) * 100);
            document.getElementById('progress-bar').value = percentComplete;
            document.getElementById('progress-text').innerText = `${percentComplete}%`;
        }
    };

    xhr.onload = function () {
        if (xhr.status === 200) {
            alert('Archivos procesados exitosamente.');
            window.location.reload();
        } else {
            alert('Error al procesar los archivos.');
        }
    };

    xhr.send(formData);
});
