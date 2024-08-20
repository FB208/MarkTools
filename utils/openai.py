# 该方法仅用于测试模型能力，不建议在生产环境中使用
from openai import OpenAI
from flask import current_app as app

def get_client():
    # 获取配置变量
    api_key = ""
    base_url = ""
    client = OpenAI(
        base_url=base_url,
        api_key=api_key
    )
    return client

def get_chat_completion(messages):
    client = get_client()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    return response

def get_json_completion(messages):
    client = get_client()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )
    return response