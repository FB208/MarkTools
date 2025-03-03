from openai import OpenAI
from flask import current_app as app
from .llm_interface import LLMInterface

class GrokLLMService(LLMInterface):
    def get_client(self):
        api_key = app.config['GROK_API_KEY']
        base_url = app.config['GROK_BASE_URL']
        client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        return client
    
    def get_messages(self, response):
        return response.choices[0].message.content

    def get_chat_completion(self, messages):
        client = self.get_client()
        response = client.chat.completions.create(
            model="grok-beta",
            messages=messages
        )
        return response

    def get_json_completion(self, messages):
        client = self.get_client()
        response = client.chat.completions.create(
            model="grok-beta",
            messages=messages,
            response_format={
                'type': 'json_object'
            }
        )
        return response
    
    def get_json_completion_v2(self, messages,response_format):
        pass