from zhipuai import ZhipuAI
from flask import current_app as app
from .llm_interface import LLMInterface

class GLMLLMService(LLMInterface):
    def get_client(self):
        api_key = app.config['ZHIPUAI_API_KEY']
        client = ZhipuAI(api_key=api_key)
        return client
    
    def get_messages(self, response):
        return response.choices[0].message.content

    def get_chat_completion(self, messages):
        client = self.get_client()
        response = client.chat.completions.create(
            model="glm-4-air",
            messages=messages
        )
        return response
    async def get_chat_completion_async(self, messages):
        client = self.get_client()
        response = await client.chat.asyncCompletions.create(
            model="glm-4-air",
            messages=messages
        )
        return response
    def get_chat_completion_async_result(self, task_id):
        client = self.get_client()
        response = client.chat.asyncCompletions.retrieve_completion_result(task_id=task_id)
        return response.task_status,response

    def get_json_completion(self, messages):
        client = self.get_client()
        response = client.chat.completions.create(
            model="glm-4-air",
            messages=messages,
            response_format={
                'type': 'json_object'
            }
        )
        return response
    
    def get_json_completion_v2(self, messages,response_format):
        pass