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
    
    user_content = [
        {
            "role": "user",
            "content": "介绍一下你自己",
            "content_type": "text"
        }

    ]
    # if file_id:
    #     user_content.append({"type": "image", "file_id": file_id})
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": json.dumps(user_content, ensure_ascii=False),
                "content_type": "text"
            }
        ]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))
    
    return response.json()

# # 使用示例
# personal_access_token = "pat_OYDacMzM3WyOWV3Dtj2bHRMymzxP****"
# uuid = "newid1234"
# user_message = "你好，这是我的图片"
# assistant_message = "你好我是一个bot"
# file_id = "{{FILE_ID}}"  # 如果没有图片，可以设置为 None

# result = create_conversation(personal_access_token, uuid, user_message, assistant_message, file_id)
# print(result)