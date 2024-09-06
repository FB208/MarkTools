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
        
        # 检查最后一条消息是否为用户消息
        if messages[-1]["role"] != "user":
            raise ValueError("最后一条消息必须是用户消息")
        
        # 提取最后一条用户消息
        last_user_message = messages[-1]["content"]
        
        # 提取 system_instruction 和 history
        system_instruction = "You are a helpful assistant."
        history = []
        for msg in messages[:-1]:  # 排除最后一条用户消息
            if msg["role"] == "system":
                system_instruction = msg["content"]
            else:
                # 将 OpenAI 的 'assistant' 转换为 Gemini 的 'model'
                role = "model" if msg["role"] == "assistant" else msg["role"]
                history.append({"role": role, "parts": [msg["content"]]})  # 修改为列表形式
        
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_instruction
        )
        chat = model.start_chat(history=history)

        return chat.send_message(last_user_message)  # 发送最后一条用户消息

    def get_json_completion(self, messages):
        self.get_client()
        model = genai.GenerativeModel('gemini-1.5-flash',generative_config={"response_mime_type": "application/json"})
        response = model.generate_content(messages)
        return response