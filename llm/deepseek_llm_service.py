from openai import OpenAI
from flask import current_app as app
from .llm_interface import LLMInterface
import re

class DeepSeekLLMService(LLMInterface):
    def get_client(self):
        api_key = app.config['DEEPSEEK_API_KEY']
        base_url = app.config['DEEPSEEK_BASE_URL']
        client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        return client
    def clear_thinking_msg(self, response):
        msg = response.choices[0].message.content
        clear_msg = re.sub(r'<think>[\s\S]*?</think>', '', msg)
        return clear_msg
    def get_messages(self, response):
        return response.choices[0].message.content

    def get_chat_completion(self, messages):
        client = self.get_client()
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        return response
    
    def get_chat_completion_async(self, messages):
        pass
    def get_chat_completion_async_result(self, task_id):
        pass

    def get_json_completion(self, messages):
        client = self.get_client()
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            response_format={
                'type': 'json_object'
            }
        )
        return response
    
    def get_json_completion_v2(self, messages,response_format):
        pass