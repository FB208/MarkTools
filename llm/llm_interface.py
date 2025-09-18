from abc import ABC, abstractmethod

class LLMInterface(ABC):
    @abstractmethod
    def get_client(self):
        pass

    @abstractmethod
    def get_messages(self, response):
        pass
    def clear_thinking_msg(self, response):
        pass
    @abstractmethod
    def get_json_completion(self, messages):
        '''
        使用示例system_prompt:
        你是一个语言学专家，擅长文字理解。
    你将会得到两段文本<OLD_TEXT>和<NEW_TEXT>，你的任务是找出<NEW_TEXT>和<OLD_TEXT>的差异，以JSON的格式输出。
    
    EXAMPLE INPUT: 
        <OLD_TEXT>
        摄影作品，闪闪发光的老虎，炯炯有神的眼睛，明媚的阳光，高清写真
        </OLD_TEXT>
        <NEW_TEXT>
        摄影作品，闪闪发光的中国龙，炯炯有神的眼睛，高清写真，脸部特写
        </NEW_TEXT>
    EXAMPLE JSON OUTPUT:
    {
        'status': 'success',
        'data': [{'new_text':'中国龙','type':'update','old_text':'老虎'},{'new_text':'','type':'delete','old_text':'明媚的阳光'},{'new_text':'脸部特写','type':'add','old_text':''}]
    }
    
    如果你认为两段文本毫无关系，则返回
    {
        'status': 'failed',
        'data': []
    }
        '''
        pass
    
    def get_json_completion(self,model, messages):
        pass    
    
    def get_json_completion_v2(self, messages):
        '''
        下面代码仅供参考
        '''
        client = self.get_client()
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "developer", 
                    "content": "You extract email addresses into JSON data."
                },
                {
                    "role": "user", 
                    "content": "Feeling stuck? Send a message to help@mycompany.com."
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "email_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "email": {
                                "description": "The email address that appears in the input",
                                "type": "string"
                            },
                            "additionalProperties": False
                        }
                    }
                }
            }
        )

        print(response.choices[0].message.content)

        pass
        

        
    @abstractmethod
    def get_chat_completion(self, messages):
        pass
    def get_chat_completion(self,model, messages):
        pass  
    @abstractmethod
    async def get_chat_completion_async(self, messages):
        """
        异步聊天完成功能
        与同步版本get_chat_completion功能相同，但是使用异步方式实现
        返回结构：id='123456789' request_id='654321' model='glm-4-plus' task_status='PROCESSING'
        """
        pass

    @abstractmethod
    def get_chat_completion_async_result(self, task_id):
        '''
        查询异步任务结果
        '''
        pass

    def get_search_chat_completion(self, messages):
        """
        搜索相关的聊天补全功能，这是一个可选实现的方法
        默认实现是直接调用普通的chat completion
        """
        return self.get_chat_completion(messages)
