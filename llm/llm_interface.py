from abc import ABC, abstractmethod

class LLMInterface(ABC):
    @abstractmethod
    def get_client(self):
        pass

    @abstractmethod
    def get_messages(self, response):
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
    
    @abstractmethod
    def get_chat_completion(self, messages):
        pass

