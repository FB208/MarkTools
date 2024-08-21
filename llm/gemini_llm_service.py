import google.generativeai as genai
from flask import current_app as app
from .llm_interface import LLMInterface

class GeminiLLMService(LLMInterface):
    def get_client(self):
        # 获取配置变量
        api_key = app.config['GOOGLE_API_KEY']
        client = genai.configure(api_key=api_key)
        return client
    
    def get_messages(self, response):
        return response.text

    def get_chat_completion(self, messages):
        client = self.get_client()
        model = client.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(messages)

        return response

    def get_json_completion(self, messages):
        client = self.get_client()
        model = client.GenerativeModel('gemini-1.5-flash',generative_config={"response_mime_type": "application/json"})
        response = model.generate_content(messages)
        return response