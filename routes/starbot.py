from flask import current_app as app
from flask import render_template, request, jsonify
from . import starbot_bp

@starbot_bp.route('/callback', methods=['POST'])
def callback():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # TODO: 处理接收到的JSON数据
        
        return jsonify({'message': 'Success', 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
