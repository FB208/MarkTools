import pytest
from llm.gemini_llm_service import GeminiLLMService
from app import create_app
from test_config import TestConfig

# 创建Flask应用
app = create_app()
app.config.from_object(TestConfig)
# pytest -s tests/llm/gemini_llm_service_test.py::test_get_chat_completion
def test_get_chat_completion():
    with app.app_context():
        messages = [
            {"role": "system", "content": "你是一个全能助手，善于回答用户提出的问题"},
            {"role": "user", "content": "讲个故事吧"}
        ]
        print(messages)
        llm_service = GeminiLLMService()
        completion = llm_service.get_chat_completion(messages)
        print(completion)
        result = llm_service.get_messages(completion)
        print(result)

# pytest -s tests/llm/gemini_llm_service_test.py::test_get_search_chat_completion
def test_get_search_chat_completion():
    with app.app_context():
        messages = [
            {"role": "system", "content": """你是一个全能助手，善于回答用户提出的问题.
             要求：
             1. 始终使用中文
             2. 像聊天一样回答问题，不要使用markdown等文本格式"""},
            {"role": "user", "content": "今天天气如何？"},
            {"role": "assistant", "content": "你在哪个城市呢？"},
            {"role": "user", "content": "我在杭州"},
        ]
        
        print("messages:",messages)
        llm_service = GeminiLLMService()
        completion = llm_service.get_search_chat_completion(messages)
        print("completion:",completion)
        for each in completion.candidates[0].content.parts:
            print("each:",each.text)
        print("grounding_metadata:",completion.candidates[0].grounding_metadata.search_entry_point.rendered_content)
