def translate_text(chinese_text, english_text, direction):
    if direction == 'zh_to_en':
        # 这里添加中文翻译为英文的逻辑
        return f"Translated to English: {chinese_text}"
    elif direction == 'en_to_zh':
        # 这里添加英文翻译为中文的逻辑
        return f"翻译成中文: {english_text}"
    else:
        return ''