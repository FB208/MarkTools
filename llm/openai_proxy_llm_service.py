from openai import OpenAI
from flask import current_app as app
from .llm_interface import LLMInterface

class OpenAIProxyLLMService(LLMInterface):
    def get_client(self):
        api_key = app.config['OPENAI_PROXY_API_KEY']
        base_url = app.config['OPENAI_PROXY_BASE_URL']
        client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        return client
    
    def get_messages(self, response):
        return response.choices[0].message.content

    def get_chat_completion(self, messages,model:str="gpt-4o-mini"):
        client = self.get_client()
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response
    def get_chat_completion_async(self, messages):
        pass
    def get_chat_completion_async_result(self, task_id):
        pass
    def get_json_completion(self, messages,model:str="gpt-4o-mini"):
        client = self.get_client()
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={
                'type': 'json_object'
            }
        )
        return response
    
    def get_json_completion_v2(self, messages,response_format):
        client = self.get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            response_format=response_format
        )
        return response
        
    
    def get_chat_completion_o1(self, messages,model:str="o1-preview"):
        client = self.get_client()
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response
    
