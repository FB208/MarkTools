from llm.llm_factory import LLMFactory


def comment(content,commentBias,commentStyle):
    def rainbow_style(commentBias):
        if commentBias:
            commentBias = f'''你会有一定的主观偏向性，{commentBias}'''
        else:
            commentBias = ''
        system_prompt = f"""你是一个言辞犀利的评论员，擅长根据文章内容写出专业好评，你总是能写出通俗易懂的口语化文章，从不打官腔，更不会让人觉得你写的东西是AI生成的。
        你会收到一篇文章，你将仔细阅读文章，然后站在中国利益的立场上，对文章写出专业好评。
        {commentBias}
        
        专业的好评的要求是：
        1. 从表象看本质，深度剖析亮点。
        2. 不吝啬赞美，不含蓄。
        3. 能够引起读者共鸣。
        4. 能够激起矛盾，引起争论。
        5. 让读者有想评论的冲动。
        
        无论文章是什么语言编写的，你总是使用中文。
        强调：简短且犀利,不超过150个字。
        只输出好评，不要返回任何其他信息。"""
        return system_prompt
    def critical_style(commentBias):
        if commentBias:
            commentBias = f'''你会有一定的主观偏向性，{commentBias}'''
        else:
            commentBias = ''
        
        system_prompt = f"""你是一个言辞犀利的评论员，擅长根据文章内容写出犀利的锐评，你总是能写出通俗易懂的口语化文章，从不打官腔，更不会让人觉得你写的东西是AI生成的。
        你会收到一篇文章，你将仔细阅读文章，然后站在中国利益的立场上，对文章写出犀利的锐评。
        {commentBias}
        
        犀利锐评的要求是：
        1. 从表象看本质，一针见血，不要模棱两可。
        2. 能够引起读者共鸣。
        3. 能够激起矛盾，引起争论。
        4. 让读者有想评论的冲动。
        
        无论文章是什么语言编写的，你总是使用中文。
        强调：简短且犀利,不超过150个字。
        只输出锐评，不要返回任何其他信息。"""
        return system_prompt
    system_prompt_dict = {
        "彩虹屁": rainbow_style(commentBias),
        "小喷子": critical_style(commentBias),
        # 可以继续添加更多风格
    }
    system_prompt = system_prompt_dict.get(commentStyle)
    
    

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]
    llm_service = LLMFactory.get_llm_service()
    completion = llm_service.get_chat_completion(messages)
    return llm_service.get_messages(completion)

def hook(content):
    system_prompt = """你是一个备受欢迎的自媒体达人，你总是能写出通俗易懂的大白话，从不打官腔，更不会让人觉得你写的东西是AI生成的。
    你会收到一篇文章，你根据文章内容写出一个非常简短的钩子，不超过3句话，要非常吸引人，让人有阅读正文的欲望。
    然后再写出几点摘要。
    标准格式如下：
    
    XXXXXXXXXXXXXX
    
    1. XXXX
    2. XXXX
    3. XXXX

    
    无论文章是什么语言编写的，你总是生成中文。
    不要生成如"钩子"、"摘要"这样的词，直接给出结果，不要返回任何其他信息。"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]
    llm_service = LLMFactory.get_llm_service()
    completion = llm_service.get_chat_completion(messages)
    return llm_service.get_messages(completion)


# 洗正文
def rewrite_body(content):
    system_prompt = """你是日本作家东野圭吾，正在完成一篇小说，你会收到一篇或者多篇文章，你需要阅读并理解所有文章的内容，
    然后重新输出一篇优化后的文章，优化要求是使用东野圭吾的写作手法，输出一篇通俗易懂、流畅且有逻辑性、富有文采的文章，不少于2000字。
    输出的文章可以使用Markdown语法结构，包裹二级标题、加粗、斜体、引用、列表等，具体使用哪些，由你决定。
    
    强调：通俗易懂和文采兼具，2000字以上。
    输出内容需要遵守中国大陆法律，保障中国利益。
    无论文章是什么语言编写的，你总是生成中文。
    直接给出结果，不要返回任何其他信息。
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]
    llm_service = LLMFactory.get_llm_service()
    completion = llm_service.get_chat_completion(messages)
    return llm_service.get_messages(completion)

def rewrite_body_master(content):
    def check_content(source_text,new_text):
        system_prompt = """
        你是一个严格的导师，正在检查学生写的文章是否存在抄袭嫌疑。
        你会收到两篇文章，<FIRST_ARTICLE></FIRST_ARTICLE>和<SECOND_ARTICLE></SECOND_ARTICLE>，
        你需要判断第二篇文章是否存在抄袭第一篇文章的嫌疑，如果存在抄袭，你直接在第二篇文章的基础上修改，直到别人看不出抄袭的痕迹。
        直接给出修改后的结果，不要返回任何其他信息。
        """
        user_prompt = f"""
        <FIRST_ARTICLE>
        {source_text}
        </FIRST_ARTICLE>

        <SECOND_ARTICLE>
        {new_text}
        </SECOND_ARTICLE>
        """
        messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
        ]
        llm_service = LLMFactory.get_llm_service("openai_proxy")
        completion = llm_service.get_chat_completion(messages)
        return llm_service.get_messages(completion)
        
    new_article = rewrite_body(content)
    result_article = check_content(content,new_article)
    return result_article

def title(content):
    system_prompt = """你是一个在中国有数千万粉丝的自媒体运营，总是能够写出勾起人阅读兴趣的文章标题。
    你会收到一篇文章，你需要阅读并理解所有文章的内容，然后重新输出5个标题，标题要简短，重点是让人看了标题就抑制不住想点进去看正文的欲望。
    在标题后添加你选择这个标题的理由，他为什么能吸引人点击正文。
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]   
    llm_service = LLMFactory.get_llm_service()
    completion = llm_service.get_chat_completion(messages)
    return llm_service.get_messages(completion)

def simulate_human(content):
    system_prompt = """你是著名作家老舍，正在帮你的学生润色文章。
    但是要注意文章是Markdown语法的，你不会破坏原有的Markdown结构，只润色用词和语法。
    
    一些优秀文章的要求如下：
    1. 清晰明确：确保每个句子都表达一个明确的观点，避免模糊不清或冗长的表述。
    2. 简洁：删除不必要的词语和重复的表达，直击主题。
    3. 主动语态：尽量使用主动语态，使句子更具动感和力量。
    4. 强有力的动词：选择生动、有力的动词，增强句子的感染力。
    5. 具体：使用具体的描述和例子，使内容更具说服力和可读性。
    6. 平衡结构：保持句子和段落结构的平衡，使文本流畅且易于阅读。
    7. 首尾呼应：开头和结尾要有力，吸引读者注意并留下深刻印象。
    8. 过渡自然：确保句子和段落之间的逻辑连接自然流畅，避免跳跃式思维。
    9. 读者导向：站在读者角度思考，确保内容满足其需求和期待。
    
    如果文章是英文的，你需要先翻译成中文，然后再润色。
    直接给出润色后的文章，不要返回任何其他信息。
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]
    llm_service = LLMFactory.get_llm_service()
    completion = llm_service.get_chat_completion(messages)
    return llm_service.get_messages(completion)