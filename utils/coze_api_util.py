import requests
import json
from flask import current_app as app
import time

# 创建会话
def conversation_create():
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

# 发起对话
def chat(conversation_id, bot_id, content):
    '''
    content示例：
    [
        {
            "type": "text",
            "text": "你好我有一个帽衫，我想问问它好看么，你帮我看看"
        }, {
            "type": "image",
            "file_id": "{{file_id_1}}"
        }, {
            "type": "file",
            "file_id": "{{file_id_2}}"
        },
        {
            "type": "file",
            "file_url": "{{file_url_1}}"
        }
    ]
    content = json.dumps(content, ensure_ascii=False)
    "[{\"type\":\"text\",\"text\":\"你好我有一个帽衫，我想问问它好看么，你帮我看看\"},{\"type\":\"image\",\"file_id\":\"{{file_id_1}}\"},{\"type\":\"file\",\"file_id\":\"{{file_id_2}}\"},{\"type\":\"file\",\"file_url\":\"{{file_url_1}}\"}]"

    '''
    url = f" https://api.coze.cn/v3/chat?conversation_id={conversation_id}"
    personal_access_token = app.config['COZE_PERSONAL_ACCESS_TOKEN']

    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "bot_id": bot_id,
        "user_id": "marktools",  # 你可能需要动态设置这个值
        "stream": False,
        "auto_save_history": True,
        "additional_messages": [
            # {
            #     "role": "user",
            #     "content": message,
            #     "content_type": "text"
            # }
            {
                "role": "user",
                "content": content,
                "content_type": "object_string"
            }
        ]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    chat_id = response.json()['data']['id']
    attempts = 0
    while attempts < 100:
        response = chat_status(conversation_id, chat_id)
        status = response['data']['status']
        
        if status != 'in_progress':
            match status:
                case 'completed':
                    response_list = chat_list(conversation_id, chat_id)
                    return chat_get_message(response_list)
                case 'failed':
                    return "error";
                case 'requires_action':
                    return "error";
                case 'canceled':
                    return "error";
        
        time.sleep(2)  # 等待2秒
        attempts += 1
    return response.json()

# 查看对话状态
def chat_status(conversation_id,chat_id):
    url = f"https://api.coze.cn/v3/chat/retrieve?chat_id={chat_id}&conversation_id={conversation_id}"
    personal_access_token = app.config['COZE_PERSONAL_ACCESS_TOKEN']
    
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    return response.json()

# 查看对话消息
def chat_list(conversation_id,chat_id):
    url = f" https://api.coze.cn/v3/chat/message/list?conversation_id={conversation_id}&chat_id={chat_id}"
    personal_access_token = app.config['COZE_PERSONAL_ACCESS_TOKEN']
    
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    return response.json()

# 获取AI最终应答的消息内容
def chat_get_message(response):
    if 'data' in response and isinstance(response['data'], list):
        for item in response['data']:
            if item.get('type') == 'answer':
                return item.get('content', '')
    return ''    
# 创建消息
def message_create(conversation_id, message):
    url = f"https://api.coze.cn/v1/conversation/message/create?conversation_id={conversation_id}"
    personal_access_token = app.config['COZE_PERSONAL_ACCESS_TOKEN']
    
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


########## 文件 ###########
# 上传文件
import requests
from flask import current_app as app

def file_upload(file):
    url = "https://api.coze.cn/v1/files/upload"
    personal_access_token = app.config['COZE_PERSONAL_ACCESS_TOKEN']
    
    headers = {
        "Authorization": f"Bearer {personal_access_token}"
    }
    
    files = {
        'file': (file.filename, file.stream, file.content_type)
    }
    
    # 发送 POST 请求
    response = requests.post(url, headers=headers, files=files)
    
    # 返回响应的 JSON 内容
    return response.json()