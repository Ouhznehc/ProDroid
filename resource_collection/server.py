from flask import Flask, request
from werkzeug.utils import secure_filename
import os
import json


app = Flask(__name__)

with open('config.json') as config_file:
    config = json.load(config_file)
    upload_folder = config['upload_folder']
    port = config['port']

app.config['UPLOAD_FOLDER'] = upload_folder

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'File uploaded successfully'

if __name__ == '__main__':
    app.run(debug=True, port=port)
