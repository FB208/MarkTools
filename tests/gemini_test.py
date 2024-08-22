import pytest
from flask import Flask
from llm.gemini_llm_service import GeminiLLMService

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['GOOGLE_API_KEY'] = '111'  # 使用测试用的 API 密钥
    return app

def test_get_chat_completion(app):
    with app.app_context():
        # 创建 GeminiLLMService 实例
        gemini_llm_service = GeminiLLMService()

        # 模拟 messages 参数
        messages = [
            {"role": "system", "content": "你是一个全能助手，善于回答用户提出的问题"},
            {"role": "user", "content": "讲个故事吧"}
        ]

        # 调用方法
        result = gemini_llm_service.get_chat_completion(messages)

        print(result)
        # 添加适当的断言
        assert False