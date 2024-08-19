from utils.deepseek import get_chat_completion

def translate_text(chinese_text, english_text, direction):
    text=""
    if direction == 'zh_to_en':
        # 这里添加中文翻译为英文的逻辑
        text = chinese_text
    elif direction == 'en_to_zh':
        # 这里添加英文翻译为中文的逻辑
        text = english_text
    else:
        print("Invalid direction")
    
    messages = [
        {"role": "system", "content": "你是一个语言学专家，擅长中英文互译。你会收到中文或英文，然后你需要返回对应的翻译。直接给出翻译结果，不要返回任何其他信息"},
        {"role": "user", "content": f"{text}"}
    ]
    return get_chat_completion(messages).choices[0].message.content

        