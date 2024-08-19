from flask import current_app as app
from flask import render_template, request, jsonify
from . import translate_bp
from services.translate_service import translate_text

@translate_bp.route('/translate_page')
def translate_page():
    return render_template('translate.html.j2',kk="asdadsdas")

@translate_bp.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    chinese_text = data.get('chinese', '')
    english_text = data.get('english', '')
    direction = data.get('direction', '')

    translation = translate_text(chinese_text, english_text, direction)
    return jsonify({'translation': translation})