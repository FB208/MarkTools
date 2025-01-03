from llm.llm_factory import LLMFactory
from utils.google_search_util import GoogleSearchUtil
import json
# 提取搜索关键词
def extract_search_keywords(text):
    system_prompt = '''
    你将会收到一段长文本，你的最终目标是理解文本并通过google搜索内容来完善文案，所以你需要先编写一段用于google搜索的关键词
    要求：
    1. 你需要理解google搜索的逻辑，搜索内容要全面，但不是细致，因为太细致可能搜不到内容
    2. 关键词要尽可能的简洁，不要使用任何修饰词
    3. 只提取文本涉及的知识点，不要泄露任何重要信息
    4. 只返回关键词，不要返回任何其他信息。

    '''
    user_prompt = f'{text}'
    
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]
    llm_service = LLMFactory.get_llm_service('openai_proxy')
    completion = llm_service.get_chat_completion(messages) 
    content = llm_service.get_messages(completion)

    return content
