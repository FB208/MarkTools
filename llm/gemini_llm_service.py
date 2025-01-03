# gemini接口格式和openai不兼容，未完成兼容调试
import google.generativeai as genai
from google import genai as genai_new
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch, Part
from flask import current_app as app
from .llm_interface import LLMInterface

class GeminiLLMService(LLMInterface):
    def get_client(self):
        # 获取配置变量
        api_key = app.config['SIMPLE_GOOGLE_API_KEY']
        genai.configure(api_key=api_key)
    
    def get_messages(self, response):
        print(response)
        return response.text

    def _process_openai_messages(self, messages):
        """
        处理OpenAI格式的消息，提取系统指令和最后的用户消息
        """
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
        
        return system_instruction, last_user_message, history

    def get_chat_completion(self, messages,model:str="gemini-1.5-flash"):
        self.get_client()
        
        system_instruction, last_user_message, history = self._process_openai_messages(messages)
        
        model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_instruction
        )
        chat = model.start_chat(history=history)

        return chat.send_message(last_user_message)  # 发送最后一条用户消息

    def get_json_completion(self, messages,model:str="gemini-1.5-flash"):
        self.get_client()
        model = genai.GenerativeModel(model_name=model,generative_config={"response_mime_type": "application/json"})
        response = model.generate_content(messages)
        return response
    
    def get_search_chat_completion(self, messages,model:str="gemini-2.0-flash-exp"):
        '''
        gemini2.0使用最新的google-genai库，和gemini1.5的库不兼容
        '''
        # 转换消息格式
        system_instruction, last_user_message, history = self._process_openai_messages(messages)
        client = genai_new.Client(http_options={'api_version': 'v1alpha'},api_key=app.config['SIMPLE_GOOGLE_API_KEY'])

        # 处理最新的history
        # chat_history = []
        # for msg in history:
        #     chat_history.append(Part.from_text(msg["parts"][0]))
        
        google_search_tool = Tool(
            google_search = GoogleSearch()
        )
        response = client.models.generate_content(
            model=model,
            contents=last_user_message,
            config=GenerateContentConfig(
                #system_instruction=system_instruction,
                tools=[google_search_tool],
                response_modalities=["TEXT"]#,
                #history=chat_history
            )
        )
        return response
