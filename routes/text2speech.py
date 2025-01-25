from flask import current_app as app
from flask import render_template, request, jsonify, send_file
from . import text2speech_bp
import edge_tts
import asyncio
import json
import os
import datetime

def ensure_temp_dir():
    """确保临时文件目录存在"""
    temp_dir = os.path.join(app.config['BASE_PATH'], 'tempfiles', 'text2speech')
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def clean_old_files(temp_dir, hours=24):
    """清理指定时间之前的临时文件"""
    now = datetime.datetime.now()
    for file in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, file)
        if os.path.isfile(file_path):
            file_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
            if (now - file_time).total_seconds() > hours * 3600:
                try:
                    os.remove(file_path)
                except OSError:
                    pass

async def get_voices():
    voices = await edge_tts.list_voices()
    voice_dict = {}
    for voice in voices:
        lang = voice["Locale"]
        if lang not in voice_dict:
            voice_dict[lang] = []
        voice_dict[lang].append({
            "name": voice["ShortName"],
            "gender": voice["Gender"],
            "display_name": f"{voice['FriendlyName']} ({voice['Gender']})"
        })
    return voice_dict

@text2speech_bp.route('/text2speech')
def text2speech():
    voices = asyncio.run(get_voices())
    return render_template('text2speech.html', voices=json.dumps(voices))

@text2speech_bp.route('/api/text2speech', methods=['POST'])
async def convert_text2speech():
    try:
        data = request.get_json()
        text = data.get('text')
        voice = data.get('voice')
        
        if not text or not voice:
            return jsonify({"error": "Missing required parameters"}), 400

        # 获取临时文件目录并清理旧文件
        temp_dir = ensure_temp_dir()
        clean_old_files(temp_dir)

        # 生成带时间戳的文件名，避免冲突
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        file_name = f"speech_{timestamp}_{hash(text + voice)}.mp3"
        output_file = os.path.join(temp_dir, file_name)
        
        # 转换文字为语音
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        
        # 直接返回文件，不尝试删除
        # 让 clean_old_files 函数在下次请求时处理清理
        return send_file(output_file, mimetype="audio/mpeg", as_attachment=True)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500