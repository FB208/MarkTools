import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_default_openai_api_key')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.deepseek.com/v1/')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'your_default_google_api_key')
    LLM_SERVICE = os.getenv('LLM_SERVICE', 'deepseek')
    # 其他配置变量