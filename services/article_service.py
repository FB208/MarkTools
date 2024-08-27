from llm.llm_factory import LLMFactory

def summary(content):
    
    system_prompt = "你是一个言辞犀利的评论员，擅长总结文章。你会收到一篇文章，然后你需要返回文章的总结。无论文章是什么语言编写的，你总是使用中文总结。直接给出总结结果，不要返回任何其他信息。"
    
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
