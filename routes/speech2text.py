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
            # text = get_text(file)
            text="""好吧，并且附赠十万个算力的头纹，拿来就能够用，就可以实练，就可以实操。你想，获得想要的所有的素材，图片，漂亮的文字，漂亮的图片，音频，还有咱们的这样的视频，统统都可以实现的，家人们。这个就是人工智能给咱们带来的所有的要素。如果，直播间的家人们，你们想学习人工智能，一定要掌握两个要素。第一个要素是什么 呀，一定要掌握学习人工智能的思维。告诉大家，学习人工智能的思维一定要持续不断地学习。第二个要素是什么呀，一定要上手去实操，去实践人工智能。只有这样的话 ，你们才能在人工智能道路上走得又快又好。好了，这些福利呢，周老师直播，下播之后，第一时间给大家安排。只需要直播间的家人们，给周老师点个关注，亮个黄心， 点击下方的小风车。然后填写相关的信息，周老师下播之后，第一时间给大家安排这些福利，好了。"""
            # 返回上传成功的信息和文件的公共URL
            return jsonify({
                'message': text
            })
        except Exception as e:
            # 如果上传过程中出现错误,返回错误信息
            return jsonify({'error': f'文件上传失败: {str(e)}'}), 500

    return render_template('speech2text.html')