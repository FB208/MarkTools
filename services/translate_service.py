from utils.openai import get_chat_completion, get_json_completion

def translate_text(chinese_text, english_text,chinese_old,english_old, direction):
    prompt=""
    translation_task=""
    origin_text=""
    if direction == 'zh_to_en':
        # 这里添加中文翻译为英文的逻辑
        translation_task = "中文到英文的翻译"
        origin_text = chinese_text
    elif direction == 'en_to_zh':
        # 这里添加英文翻译为中文的逻辑
        translation_task = "英文到中文的翻译"
        origin_text = english_text
    else:
        print("Invalid direction")
    
    if not chinese_text and not english_text:
        if direction == 'zh_to_en':
            diff_json = extract_content(chinese_old, chinese_text)
            system_prompt = f"""你的任务是中文到英文的翻译，你将会得到三段由xml标签包裹的文本，<OLD_CHINESE>是中文原文，<OLD_ENGLISH>是<OLD_CHINESE>翻译后的英文，
            <TRANSLATE_TEXT>是基于<OLD_CHINESE>修改而来中文文本。
            还有一段json格式的数据，是<TRANSLATE_TEXT>和<OLD_CHINESE>的差异指示。
            你需要参照json中的'data'，来修改<OLD_ENGLISH>，得到新的英文翻译，json中没有提到的内容，完全按照<OLD_ENGLISH>输出，不做任何改变。
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
        # prompt = f"""你的任务是{translation_task}，你将会得到三段文本，均用xml标签包裹，<OLD_CHINESE></OLD_CHINESE>是中文原文，<OLD_ENGLISH></OLD_ENGLISH>是英文原文，<NEW_TEXT></NEW_TEXT>是要目标文本， 
        #     你需要基于'中文原文'和'英文原文'来完成'目标文本'的翻译。 
        #     # 步骤
        #     1. 对比'目标文本'和'中文原文'，找出被修改的部分
        #     2. 翻译被修改的部分
        #     3. 将翻译结果替换'英文原文'中被修改的部分，并保证翻译结果的语法和语义正确
            
        #     # 提供给你的数据如下
        #     <OLD_CHINESE> 
        #         {chinese_text} 
        #     </OLD_CHINESE> 
            
        #     <OLD_ENGLISH> 
        #         {english_text} 
        #     </OLD_ENGLISH> 
            
        #     <NEW_TEXT> 
        #         {origin_text}
        #     </NEW_TEXT> 
            
        #     除了翻译结果，不要返回任何其他信息。
        #     """
    else:
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
   
    return get_chat_completion(messages).choices[0].message.content

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
    completion = get_json_completion(messages)
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

