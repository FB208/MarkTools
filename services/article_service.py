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
    强调：简短且犀利,不超过150个字。
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
    
    1. XXXX
    2. XXXX
    3. XXXX

    
    无论文章是什么语言编写的，你总是生成中文。
    不要生成如“钩子”、“摘要”这样的词，直接给出结果，不要返回任何其他信息。"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]
    llm_service = LLMFactory.get_llm_service()
    completion = llm_service.get_chat_completion(messages)
    return llm_service.get_messages(completion)


# 洗正文
def rewrite_body(content):
    system_prompt = """你是日本作家东野圭吾，正在完成帮人优化文案的工作，你会收到一篇或者多篇文章，你需要阅读并理解所有文章的内容，
    然后重新输出一篇优化后的文章，优化要求是使用东野圭吾的写作手法，输出一篇通俗易懂、流畅且有逻辑性、富有文采的文章。
    输出的文章可以使用Markdown语法结构，包裹二级标题、加粗、斜体、引用、列表等，具体使用哪些，由你决定。
    
    强调：通俗易懂和文采兼具。
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
        llm_service = OpenAILLMService()
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