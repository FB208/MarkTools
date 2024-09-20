import json
import os
from llm.llm_factory import LLMFactory
from flask import current_app as app

def history_chat():
    
    messages = return_history()
    llm_service = LLMFactory.get_llm_service("openai")
    completion = llm_service.get_chat_completion(messages)
    new_message = llm_service.get_messages(completion)
    # 将新消息追加到历史记录中
    messages.append({"role": "assistant", "content": new_message})
    # 将更新后的历史记录写入文件
    json_file_path = os.path.join(app.config['BASE_PATH'], 'static', 'json','chat', 'chat_history.json')
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(messages, file, ensure_ascii=False, indent=2)
    
    return new_message


def return_history():
    json_file_path = os.path.join(app.config['BASE_PATH'], 'static', 'json','chat', 'chat_history.json')
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            history = json.load(file)
        return history
    except FileNotFoundError:
        print(f"错误：找不到文件 {json_file_path}")
        return []
    except json.JSONDecodeError:
        print(f"错误：无法解析 JSON 文件 {json_file_path}")
        return []