# gemini接口格式和openai不兼容，未完成兼容调试
import google.generativeai as genai
from flask import current_app as app
from .llm_interface import LLMInterface

class GeminiLLMService(LLMInterface):
    def get_client(self):
        # 获取配置变量
        api_key = app.config['GOOGLE_API_KEY']
        genai.configure(api_key=api_key)
    
    def get_messages(self, response):
        return response.text

    def get_chat_completion(self, messages):
        self.get_client()
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(messages)

        return response

    def get_json_completion(self, messages):
        self.get_client()
        model = genai.GenerativeModel('gemini-1.5-flash',generative_config={"response_mime_type": "application/json"})
        response = model.generate_content(messages)
        return response