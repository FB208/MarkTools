from llm.llm_factory import LLMFactory

def simple_chat(text):
    
    system_prompt = f"""
    你是一个资深文案编辑，正在word文档上编写报告，你将收到一段文案，请优化文案，并基于现有内容扩写文案。
    要求：
    1. 不能改变原文含义
    2. 原为提到的关键信息都必须保留，你在此基础上补充你认为不完善的内容
    3. 整体优化文案，使其更加通顺，更加符合中文表达习惯
    4. 不要使用奇怪的连接词，使文章更像人类作家写的，而不是AI生成的，你可以模仿这几个作家：“余华、陈忠实、莫言”
    5. 返回符合word文档格式的内容，不要使用markdown
    6. 始终使用中文
    7. 不要返回任何其他信息，只返回文案内容
    
    """
    user_prompt = f"{text}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    llm_service = LLMFactory.get_llm_service("grok")
    completion = llm_service.get_chat_completion(messages)
    return llm_service.get_messages(completion)

# 排查逻辑漏洞
def logic_vulnerability(text):
    system_prompt = f"""
    你是一个非常仔细文案编辑，正在word文档上编写报告，你将收到一段文案，仔细阅读并分析文章中可能存在的逻辑漏洞、事实错误和错别字。
    要求：
    1. 输出原文及优化建议
    2. 返回符合word文档格式的内容，不要使用markdown
    3. 始终使用中文
    4. 按点返回你发现的问题，除此之外不要返回任何其他信息
    
    """
    user_prompt = f"{text}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    llm_service = LLMFactory.get_llm_service("deepseek")
    completion = llm_service.get_chat_completion(messages)
    return llm_service.get_messages(completion)


def inspiration2outline(text):
    print(text)
    system_prompt = f"""
    请将以下文本转换为结构化的提纲格式。要求：
    """
    user_prompt = f"{text}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    llm_service = LLMFactory.get_llm_service("grok")
    completion = llm_service.get_chat_completion(messages)
    print(llm_service.get_messages(completion))
    return llm_service.get_messages(completion)

    
