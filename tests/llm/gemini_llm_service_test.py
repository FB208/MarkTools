import pytest
from llm.gemini_llm_service import GeminiLLMService
from app import create_app
from test_config import TestConfig

# 创建Flask应用
app = create_app()
app.config.from_object(TestConfig)
# pytest tests/llm/gemini_llm_service_test.py::test_get_chat_completion
def test_get_chat_completion():
    with app.app_context():
        messages = [
            {"role": "system", "content": "你是一个全能助手，善于回答用户提出的问题"},
            {"role": "user", "content": "讲个故事吧"}
        ]
        llm_service = GeminiLLMService()
        completion = llm_service.get_chat_completion(messages)
        print(completion)
        result = llm_service.get_messages(completion)
        print(result)