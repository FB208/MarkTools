from flask import current_app as app
from flask import render_template, request, jsonify
from . import article_bp
from services.article_service import summary

@article_bp.route('/rewrite')
def rewrite():
    return render_template('rewrite.html')

@article_bp.route('/rewrite', methods=['POST'])
def do_rewrite():
    data = request.get_json()
    content = data.get('content', '')
    translate = data.get('translate', False)
    
    print(f"接收到的内容: {content}")
    print(f"是否需要翻译: {translate}")
    
    summary_content = summary(content)
    print(f"总结的内容: {summary_content}")
    # 这里可以添加您的洗稿逻辑
    rewritten_content = content  # 暂时直接返回原内容
    
    
    return jsonify({'rewritten_content': summary_content})