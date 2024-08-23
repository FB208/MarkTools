from flask import current_app as app
from flask import render_template,request,jsonify
from werkzeug.utils import secure_filename
import uuid
import base64
import os
from services.speech2text_service import get_text
from . import speech2text_bp

@speech2text_bp.route('/speech2text')
def speech2text():
    return render_template('speech2text.html')

@speech2text_bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        
        try:
            text = get_text(file)
            
            # 返回上传成功的信息和文件的公共URL
            return jsonify({
                'message': text
            })
        except Exception as e:
            # 如果上传过程中出现错误,返回错误信息
            return jsonify({'error': f'文件上传失败: {str(e)}'}), 500

    return render_template('speech2text.html')