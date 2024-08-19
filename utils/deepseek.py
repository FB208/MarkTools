from openai import OpenAI
from flask import current_app as app

def get_client():
    # 获取配置变量
    api_key = app.config['OPENAI_API_KEY']
    base_url = app.config['OPENAI_BASE_URL']
    client = OpenAI(
        base_url=base_url,
        api_key=api_key
    )
    return client

def get_chat_completion(messages):
    client = get_client()
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    return response