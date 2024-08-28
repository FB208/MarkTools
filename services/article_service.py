from llm.llm_factory import LLMFactory
from llm.openai_llm_service import OpenAILLMService

def comment(content):
    
    system_prompt = """你是一个言辞犀利的评论员，擅长根据文章内容写出犀利的锐评，你总是能写出通俗易懂的口语化文章，从不打官腔，更不会让人觉得你写的东西是AI生成的。
    你会收到一篇文章，你将仔细阅读文章，然后站在中国利益的立场上，对文章写出犀利的锐评。
    
    犀利锐评的要求是：
    1. 从表象看本质，一针见血，不要模棱两可。
    2. 能够引起读者共鸣。
    3. 能够激起矛盾，引起争论。
    4. 让读者有想评论的冲动。
    
    无论文章是什么语言编写的，你总是使用中文。
    强调：简短且犀利。
    只输出锐评，不要返回任何其他信息。"""
    

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]
    llm_service = OpenAILLMService()
    completion = llm_service.get_chat_completion(messages)
    return llm_service.get_messages(completion)

def hook(content):
    system_prompt = """你是一个备受欢迎的自媒体达人，你总是能写出通俗易懂的大白话，从不打官腔，更不会让人觉得你写的东西是AI生成的。
    你会收到一篇文章，你根据文章内容写出一个非常简短的钩子，不超过3句话，要非常吸引人，让人有阅读正文的欲望。
    然后再写出几点摘要。
    标准格式如下：
    
    XXXXXXXXXXXXXX
    
    # 要点速览
    1. XXXX
    2. XXXX
    3. XXXX

    
    无论文章是什么语言编写的，你总是生成中文。
    直接给出结果，不要返回任何其他信息。"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]
    llm_service = LLMFactory.get_llm_service()
    completion = llm_service.get_chat_completion(messages)
    return llm_service.get_messages(completion)

def simulate_human(content):
    system_prompt = """你是一个有个性的人，擅长帮人改文章，你收到的文章都是AI生成的，你需要把他们改得更像人话。
    但是要注意文章是Markdown语法的，你不会破坏原有的Markdown结构，只修改文字内容。
    直接给出结果，不要返回任何其他信息。
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]
    llm_service = LLMFactory.get_llm_service()
    completion = llm_service.get_chat_completion(messages)
    return llm_service.get_messages(completion)