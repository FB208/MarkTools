import os
from .gemini_llm_service import GeminiLLMService
from .openai_llm_service import OpenAILLMService
from .deepseek_llm_service import DeepSeekLLMService
from flask import current_app as app

class LLMFactory:
    @staticmethod
    def get_llm_service():
        service_type = app.config['LLM_SERVICE']
        # 暂不支持切换，各模型能力不同，优先使用deepseek,在他不满足的时候会使用适当能力的模型
        # return DeepSeekLLMService()
        return {
            'gemini': GeminiLLMService(),
            'openai': OpenAILLMService(),
            'deepseek': DeepSeekLLMService()
        }.get(service_type, DeepSeekLLMService())