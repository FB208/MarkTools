import requests
import json
from flask import current_app as app

def create_conversation():
    url = "https://api.coze.cn/v1/conversation/create"
    personal_access_token = app.config['COZE_PERSONAL_ACCESS_TOKEN']
    
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json"
    }
    
    # 如果需要发送请求体，可以在这里添加
    payload = {}
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    return response.json()

def send_message_to_coze(conversation_id, message, personal_access_token):
    url = f"https://api.coze.cn/v1/conversation/message/create?conversation_id={conversation_id}"
    
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "role": "user",
        "content": message,
        "content_type": "text"
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    return response.json()


