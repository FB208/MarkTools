import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_default_openai_api_key')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.deepseek.com/v1/')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'your_default_google_api_key')
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT', 'meta-buckeye-433400-c6')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'google_credentials/meta-buckeye-433400-c6-109fbeae7021.json')
    BUCKET_NAME = os.getenv('BUCKET_NAME', 'speech-audio-mark')
    LLM_SERVICE = os.getenv('LLM_SERVICE', 'deepseek')
    COZE_PERSONAL_ACCESS_TOKEN = os.getenv('COZE_PERSONAL_ACCESS_TOKEN', 'your_default_coze_personal_access_token')
    # 其他配置变量