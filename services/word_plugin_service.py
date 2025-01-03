from llm.llm_factory import LLMFactory
from services.google_search_service import extract_search_keywords

# 简单优化
def simple_optimize(text):
    system_prompt = f"""
    你是一个资深文案编辑，正在word文档上编写报告，你会按照如下要求优化收到的文案：
    
    1. 理解原文意思，根据你的专业经验来补充内容，让文章更加丰满
    2. 为了优化文案，你可以删除个别词语和句子，但原文提到的关键信息都必须保留，禁止删除关键信息
    3. 修正错别字和语病
    4. 整体优化文案，使其更加通顺，符合中国政府工作报告的表达习惯
    5. 不要使用奇怪的连接词，使文章更像人类作家写的，而不是AI生成的，你可以模仿这几个作家：“余华、陈忠实、莫言”
    6. 返回符合word文档格式的内容，不要使用markdown
    7. 始终使用中文
    8. 维护中国的权益，遵守中国法律
    9. 直接返回优化后的文案，不要返回任何其他信息
    
    """
    user_prompt = f"{text}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    llm_service = LLMFactory.get_llm_service("openai_proxy")
    completion = llm_service.get_chat_completion(messages)
    return llm_service.get_messages(completion)


# 超级扩写
def super_expand(text, search_results):
    
    system_prompt = f"""
    你是一个资深的文案编辑，负责扩写文章，你将收到几段文本，包括：需要改写的原文，用xml标记<text></text>包裹；供你参考的互联网搜索结果，用xml标记<search></search>包裹，注意<search></search>可能有多段，代表多个搜索结果。
    
    你需要按照以下步骤执行：
    1. 理解原文意思
    2. 分析搜索结果，和原文比对，如果内容有帮助则应用到扩写结果中，如果与原文意思有很大差别，你可以自己觉得是不是使用这段搜索结果
    3. 结合你丰富的经验，扩写文章，使其更加完整

    要求如下：
    1. 始终使用中文，扩写结果要符合中文语言习惯
    2. 文章要用词优美，文笔流畅，逻辑清晰，结构合理，适用于中国政府工作报告
    3. 每段之间不要使用奇怪的连接词，要自然过渡
    4. 要像一篇文章，可以适当使用一些标题，但不要分成很多点
    5. 返回符合word文档格式的内容，不要使用markdown格式
    6. 不少于2000字
    7. 直接返回扩写后的文案，不要返回任何其他信息
    
    
    """
    user_prompt = f"""
    <text>{text}</text>
    {
        ''.join([f'<search>{result}</search>' for result in search_results])
    }
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    llm_service = LLMFactory.get_llm_service("openai_proxy")
    completion = llm_service.get_chat_completion(messages)
    return llm_service.get_messages(completion)




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
    llm_service = LLMFactory.get_llm_service("openai_proxy")
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
    llm_service = LLMFactory.get_llm_service("openai_proxy")
    completion = llm_service.get_chat_completion(messages)
    print(llm_service.get_messages(completion))
    return llm_service.get_messages(completion)

    
