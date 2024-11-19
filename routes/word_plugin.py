from flask import render_template, request, jsonify
from . import word_plugin_bp

@word_plugin_bp.route('/word_plugin/home')
def home():
    """单词插件页面"""
  
    return render_template('word_plugin/home.html')


@word_plugin_bp.route('/word_plugin/simple_chat', methods=['POST'])
def simple_chat():
    return jsonify({'message': 'Hello, World!'})

