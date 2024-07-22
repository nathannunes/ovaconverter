from flask import Flask, request, send_file
import os

from werkzeug.utils import secure_filename

from extract import convert_ova_to_qcow2

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



@app.route('/')
def upload_file():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload OVA File</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #f3ec78, #af4261);
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .upload-container {
                background: rgba(255, 255, 255, 0.8);
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                text-align: center;
                transition: transform 0.3s ease-in-out;
            }
            .upload-container:hover {
                transform: scale(1.05);
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
            }
            input[type="file"] {
                display: none;
            }
            label {
                background-color: #6c63ff;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s ease-in-out;
            }
            label:hover {
                background-color: #5753c9;
            }
            input[type="submit"] {
                background-color: #6c63ff;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s ease-in-out;
            }
            input[type="submit"]:hover {
                background-color: #5753c9;
            }
            .loader {
                border: 4px solid #f3f3f3;
                border-radius: 50%;
                border-top: 4px solid #6c63ff;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                display: none;
                margin: 20px auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .file-info {
                margin-top: 10px;
            }
            .file-info span {
                display: block;
                margin-top: 10px;
            }
            .remove-file {
                color: #6c63ff;
                cursor: pointer;
                text-decoration: underline;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="upload-container">
            <h1>Upload OVA File</h1>
            <form id="upload-form" action="/convert" method="post" enctype="multipart/form-data">
                <input type="file" name="file" id="file" accept=".ova">
                <label for="file">Choose a file</label>
                <div class="file-info" id="file-info"></div>
                <br>
                <input type="submit" value="Upload and Convert">
            </form>
            <div class="loader" id="loader"></div>
        </div>
        <script>
            const fileInput = document.getElementById('file');
            const fileInfo = document.getElementById('file-info');
            const form = document.getElementById('upload-form');
            const loader = document.getElementById('loader');

            fileInput.addEventListener('change', () => {
                const file = fileInput.files[0];
                if (file) {
                    fileInfo.innerHTML = `
                        <span>${file.name}</span>
                        <span class="remove-file" id="remove-file">Remove file</span>
                    `;
                    document.getElementById('remove-file').addEventListener('click', () => {
                        fileInput.value = '';
                        fileInfo.innerHTML = '';
                    });
                } else {
                    fileInfo.innerHTML = '';
                }
            });

            form.onsubmit = function(event) {
                event.preventDefault();
                loader.style.display = 'block';

                const formData = new FormData(form);
                fetch('/convert', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.blob())
                .then(blob => {
                    loader.style.display = 'none';
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = 'converted.qcow2';
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                })
                .catch(() => {
                    loader.style.display = 'none';
                    alert('An error occurred during the conversion process.');
                });
            };
        </script>
    </body>
    </html>
    '''


@app.route('/convert', methods=['POST'])
def convert_file():
    app.logger.info('Received request: %s', request)
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = secure_filename(file.filename)
        ova_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(ova_path)
        qcow2_output_path = os.path.join(UPLOAD_FOLDER, filename.replace('.ova', '.qcow2'))
        convert_ova_to_qcow2(ova_path, qcow2_output_path)
        return send_file(qcow2_output_path, as_attachment=True)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
