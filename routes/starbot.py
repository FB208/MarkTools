from flask import current_app as app
from flask import render_template, request, jsonify
from . import starbot_bp
from services.starbot_api_service import StarBotAPIService
from services.starbot_service import single_user_reply


@starbot_bp.route('/callback', methods=['POST'])
def callback():
    '''
    接收微信消息
    '''
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        event = data.get('event')
        match event:
            case '10001':
                '''
                有新账号登录成功，重新加载所有缓存
                '''
                starbot_api_service = StarBotAPIService()
                starbot_api_service.get_account_list()
                starbot_api_service.get_robot_info()
                starbot_api_service.get_group_list()
                starbot_api_service.get_friend_list()
            case '10002':
                '''
                收到私聊消息
                '''
                
                fromWxId=data.get('fromWxId')
                fromNickName=data.get('fromNickName')
                message=data.get('message')
                response_content = single_user_reply(wx_id=fromWxId,content=message)
                
            case _:
                # 处理默认情况
                pass
        
        return jsonify({'message': 'Success', 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
