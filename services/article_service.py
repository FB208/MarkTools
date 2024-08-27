from llm.llm_factory import LLMFactory

def comment(content):
    
    system_prompt = """你是一个言辞犀利的评论员，擅长根据文章内容写出犀利的评价。
    你会收到一篇文章，你将仔细阅读文章，然后站在中国利益的立场上，对文章写出犀利的评语。
    
    犀利评语的要求是：
    1. 从表象看本质，一针见血，不要模棱两可。
    2. 能够引起读者共鸣。
    3. 能够激起矛盾，引起争论。
    4. 让读者有想评论的冲动。
    
    无论文章是什么语言编写的，你总是使用中文总结。
    直接给出总结结果，不要返回任何其他信息。"""
    
    user_prompt = f"""
    文章内容：
    '''
    {content}
    '''
    总结：
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]
    llm_service = LLMFactory.get_llm_service()
    completion = llm_service.get_chat_completion(messages)
    return llm_service.get_messages(completion)
