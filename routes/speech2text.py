from flask import current_app as app
from flask import render_template,request,jsonify
from werkzeug.utils import secure_filename
import os
from utils.coze_api_util import file_upload
from . import speech2text_bp

@speech2text_bp.route('/speech2text')
def speech2text():
    return render_template('speech2text.html')

@speech2text_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file:
            # 直接调用 Coze API 上传文件
            result = file_upload(file)
            return jsonify(result)
    return render_template('upload.html')