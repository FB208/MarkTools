import os
from .gemini_llm_service import GeminiLLMService
from .openai_llm_service import OpenAILLMService
from .deepseek_llm_service import DeepSeekLLMService
from .grok_llm_service import GrokLLMService
from flask import current_app as app

class LLMFactory:
    @staticmethod
    def get_llm_service(service_type=None):
        if service_type is None:
            service_type = app.config['LLM_SERVICE']
        return {
            'gemini': GeminiLLMService(),
            'openai': OpenAILLMService(),
            'deepseek': DeepSeekLLMService(),
            'grok': GrokLLMService()
        }.get(service_type, DeepSeekLLMService())