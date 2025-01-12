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
        inner_data = data.get('data')
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
                messageSource = inner_data.get('messageSource')
                # 不处理自己发送的消息
                if messageSource == 1:return jsonify({'message': 'Success', 'data': {}}), 200
                messageType = inner_data.get('messageType')
                robotId = inner_data.get('robotId')
                fromWxId=inner_data.get('fromWxId')
                response_content = '暂不支持此消息类型'
                match messageType:
                    case 1:
                        # 文本消息

                        # fromNickName=inner_data.get('fromNickName')
                        message=inner_data.get('message')
                        response_content = single_user_reply(wx_id=fromWxId,content=message)
                        
                    case 3:
                        # 图片消息
                        pass
                    case 34:
                        # 语音消息
                        pass
                    case _:
                        pass
                starbot_api_service = StarBotAPIService()
                starbot_api_service.send_text_message(robotId, fromWxId, response_content)
            case _:
                # 处理默认情况
                pass
        
        return jsonify({'message': 'Success', 'data': data}), 200
    except Exception as e:
        print(jsonify({'error': str(e)}))
        return jsonify({'error': str(e)}), 500
