import os

class Config:
    BASE_PATH = os.getenv('BASE_PATH', '/app')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_default_openai_api_key')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.deepseek.com/v1/')
    GROK_API_KEY = os.getenv('GROK_API_KEY', 'your_default_grok_api_key')
    GROK_BASE_URL = os.getenv('GROK_BASE_URL', 'https://api.grok.com/v1/')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'your_default_deepseek_api_key')
    DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1/')
    SIMPLE_GOOGLE_API_KEY = os.getenv('SIMPLE_GOOGLE_API_KEY', 'your_default_SIMPLE_GOOGLE_API_KEY')
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT', 'meta-buckeye-433400-c6')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'google_credentials/meta-buckeye-433400-c6-109fbeae7021.json')
    BUCKET_NAME = os.getenv('BUCKET_NAME', 'speech-audio-mark')
    LLM_SERVICE = os.getenv('LLM_SERVICE', 'deepseek')
    COZE_PERSONAL_ACCESS_TOKEN = os.getenv('COZE_PERSONAL_ACCESS_TOKEN', 'your_default_coze_personal_access_token')
    MEM0AI_API_KEY = os.getenv('MEM0AI_API_KEY', 'your_default_mem0ai_api_key')
    VIKA_API_TOKEN = os.getenv('VIKA_API_TOKEN', 'your_default_vika_api_token')
    VIKA_SPACE_ID = os.getenv('VIKA_SPACE_ID', 'your_default_vika_space_id')
  #   VIKA_DATASHEET_ID = os.getenv('VIKA_DATASHEET_ID', 'your_default_vika_datasheet_id')
    REDIS_URL = os.getenv('REDIS_URL', 'your_default_redis_url')
    MYSQL = os.getenv('MYSQL', 'your_default_mysql')
    # 其他配置变量