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
        pass
    
    @abstractmethod
    def get_chat_completion(self, messages):
        pass
