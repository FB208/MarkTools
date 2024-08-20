from flask import current_app as app
from flask import render_template, request, jsonify
from . import translate_bp
from services.translate_service import translate_text
from werkzeug.wrappers.response import ResponseStream

@translate_bp.route('/translate')
def translate():
    return render_template('translate.html',kk="asdadsdas")


@translate_bp.route('/do_translate', methods=['POST'])
def do_translate():
    data = request.get_json()
    chinese_text = data.get('chinese', '')
    english_text = data.get('english', '')
    chinese_old = data.get('chinese_old', '')
    english_old = data.get('english_old', '')
    direction = data.get('direction', '')

    translation = translate_text(chinese_text, english_text, chinese_old, english_old, direction)
    return jsonify({'translation': translation})