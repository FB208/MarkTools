from llm.llm_factory import LLMFactory

def translate_text(chinese_text, english_text,chinese_old,english_old, direction):
    # 中英文都不为空，表示是二次翻译
    if not chinese_text and not english_text:
        if direction == 'zh_to_en':
            diff_json = extract_content(chinese_old, chinese_text)
            system_prompt = f"""你的任务是中文到英文的翻译，你将会得到三段由xml标签包裹的文本，<OLD_CHINESE>是中文原文，<OLD_ENGLISH>是<OLD_CHINESE>翻译后的英文，
            <TRANSLATE_TEXT>是基于<OLD_CHINESE>修改而来中文文本。
            还有一段json格式的数据，是<TRANSLATE_TEXT>和<OLD_CHINESE>的差异指示。
            你需要参照json中的'data'，来修改<OLD_ENGLISH>，来得到新的英文翻译，json中没有提到的内容，完全按照<OLD_ENGLISH>输出，不做任何改变。
            直接给出修改后的英文，不要返回任何其他信息。"""
            user_prompt = f"""
            <OLD_CHINESE>
            {chinese_old}
            </OLD_CHINESE>
            
            <OLD_ENGLISH>
            {english_old}
            </OLD_ENGLISH>
            
            <TRANSLATE_TEXT>
            {chinese_text}
            </TRANSLATE_TEXT>
            
            差异指示json如下：
            {diff_json}
            """
        else:
            diff_json = extract_content(english_old, english_text)
            system_prompt = f"""你的任务是英文到中文的翻译，你将会得到三段由xml标签包裹的文本，<OLD_ENGLISH>是英文原文，<OLD_CHINESE>是<OLD_ENGLISH>翻译后的中文，
            <TRANSLATE_TEXT>是基于<OLD_ENGLISH>修改而来英文文本。
            还有一段json格式的数据，是<TRANSLATE_TEXT>和<OLD_ENGLISH>的差异指示。
            你需要参照json中的'data'，来修改<OLD_CHINESE>，来得到新的英文翻译，json中没有提到的内容，完全按照<OLD_CHINESE>输出，不做任何改变。
            直接给出修改后的中文，不要返回任何其他信息。"""
            user_prompt = f"""
            <OLD_ENGLISH>
            {english_old}
            </OLD_ENGLISH>
            
            <OLD_CHINESE>
            {chinese_old}
            </OLD_CHINESE>

            <TRANSLATE_TEXT>
            {english_text}
            </TRANSLATE_TEXT>
            差异指示json如下：
            {diff_json}
            """
    else:
        translation_task=""
        origin_text=""
        if direction == 'zh_to_en':
        # 这里添加中文翻译为英文的逻辑
            translation_task = "中文到英文的翻译"
            origin_text = chinese_text
        else:
        # 这里添加英文翻译为中文的逻辑
            translation_task = "英文到中文的翻译"
            origin_text = english_text
        system_prompt="你是一个语言学专家，擅长中英文互译。你会收到中文或英文，然后你需要返回对应的翻译。直接给出翻译结果，不要返回任何其他信息。"
        user_prompt = f"""你的任务是{translation_task}，要翻译的内容是三重引号(''')中的内容 
        ''' 
        {origin_text} 
        ''' 
        除了翻译结果，不要返回任何其他信息。 
        """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    llm_service = LLMFactory.get_llm_service()
    completion = llm_service.get_chat_completion(messages,model="gemini-2.5-flash-lite")
    return llm_service.get_messages(completion)

def extract_content(old_text, new_text):
    user_prompt = f"""
        <OLD_TEXT>
        {old_text}
        </OLD_TEXT>
        <NEW_TEXT>
        {new_text}
        </NEW_TEXT>
        """
    system_prompt = """你是一个语言学专家，擅长文字理解。
    你将会得到两段文本<OLD_TEXT>和<NEW_TEXT>，你的任务是找出<NEW_TEXT>和<OLD_TEXT>的差异，以JSON的格式输出。
    
    EXAMPLE INPUT: 
        <OLD_TEXT>
        摄影作品，闪闪发光的老虎，炯炯有神的眼睛，明媚的阳光，高清写真
        </OLD_TEXT>
        <NEW_TEXT>
        摄影作品，闪闪发光的中国龙，炯炯有神的眼睛，高清写真，脸部特写
        </NEW_TEXT>
    EXAMPLE JSON OUTPUT:
    {
        'status': 'success',
        'data': [{'new_text':'中国龙','type':'update','old_text':'老虎'},{'new_text':'','type':'delete','old_text':'明媚的阳光'},{'new_text':'脸部特写','type':'add','old_text':''}]
    }
    
    如果你认为两段文本毫无关系，则返回
    {
        'status': 'failed',
        'data': []
    }
    """
    messages = [
        {"role": "system", "content": f"{system_prompt}"},
        {"role": "user", "content": f"{user_prompt}"}
    ]
    llm_service = LLMFactory.get_llm_service()
    completion = llm_service.get_json_completion(messages,model="gemini-2.5-flash-lite")
    return llm_service.get_messages(completion)


def expert_translate(text):
    # 初始翻译
    def initial_translation(text):
        system_message = f"你是语言专家，擅长将英文翻译为中文"
        user_prompt = f"""下面三重引号(''')中的文本是英文，你需要将它翻译为中文。
        原文如果是Markdown格式，翻译结果不要破坏原文的格式，原文中的代码不用翻译，直接输出。
        除了翻译结果之外，不要提供任何解释或文本。
        英文如下:'''{text}'''
        """
        messages = [
            {"role": "system", "content": f"{system_message}"},
            {"role": "user", "content": f"{user_prompt}"}
        ]
        llm_service = LLMFactory.get_llm_service()
        completion = llm_service.get_chat_completion(messages,model="gemini-2.5-flash-lite")
        return llm_service.get_messages(completion)
    # 反思翻译  
    def reflect_on_translation(source_text, translation_text):
        system_message = f"""你是语言专家，擅长将英文翻译为中文。
        你将获得源文本及其翻译，您的目标是改进翻译。"""
        user_prompt = f"""
        你的任务是仔细阅读一篇源文本和一篇从英文到中文的译文，然后给出建设性的批评和有用的建议来改进译文。
        译文的最终风格和语气应该和中文口语的风格相匹配。
        
        由XML标记<SOURCE_TEXT></SOURCE_TEXT>和<TRANSLATION></TRANSLATION>分隔的源文本和初始翻译如下：

        <SOURCE_TEXT>
        {source_text}
        </SOURCE_TEXT>

        <TRANSLATION>
        {translation_text}
        </TRANSLATION>

        写建议时，注意是否有办法根据以下几点提高译文质量 
        1. 准确性(是否有添加、误译、遗漏或未翻译文本的错误),
        2. 流畅(应用中文语法、拼写和标点规则，并避免不必要的重复,
        3. 风格(翻译应反映源文本的风格并考虑文化背景),
        4. 术语(通过确保术语使用一致并反映源文本域；并确保使用中文的等效成语)。

        写一份具体的、有用的和建设性的建议清单，以改进翻译。
        """
        messages = [
            {"role": "system", "content": f"{system_message}"},
            {"role": "user", "content": f"{user_prompt}"}
        ]
        llm_service = LLMFactory.get_llm_service()
        completion = llm_service.get_chat_completion(messages,model="gemini-2.5-flash-lite")
        return llm_service.get_messages(completion)
      
    # 最终翻译
    def improve_translation(source_text, translation_text, reflection):
        system_message = f"你是语言专家，从事中文到英文的翻译和编辑工作。"

        user_prompt = f"""你的任务是仔细阅读源文本、初始翻译和语言学专家家建议，充分考虑语言学专家家建议，然后重新编辑初始翻译，输出最终翻译。
                源文本、初始翻译和语言学专家家建议由XML标记<SOURCE_TEXT></SOURCE_TEXT>、<TRANSLATION></TRANSLATION>和<EXPERT_SUGGESTIONS></EXPERT_SUGGESTIONS>分隔，内容如下：

                <SOURCE_TEXT>
                {source_text}
                </SOURCE_TEXT>

                <TRANSLATION>
                {translation_text}
                </TRANSLATION>

                <EXPERT_SUGGESTIONS>
                {reflection}
                </EXPERT_SUGGESTIONS>

                只输出新翻译，没有其他内容。"""
        messages = [
            {"role": "system", "content": f"{system_message}"},
            {"role": "user", "content": f"{user_prompt}"}
        ]
        llm_service = LLMFactory.get_llm_service()
        completion = llm_service.get_chat_completion(messages,model="gemini-2.5-flash-lite")
        return llm_service.get_messages(completion)
    
    translate_text = initial_translation(text)
    print(translate_text)
    reflection = reflect_on_translation(text,translate_text)
    print(reflection)
    result = improve_translation(text,translate_text,reflection)
    print(result)
    return result
