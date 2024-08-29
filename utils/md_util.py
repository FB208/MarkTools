import re

def remove_markdown_links(text):
    # 匹配Markdown链接的正则表达式
    pattern = r'\[([^\]]+)\]\([^\)]+\)'
    
    # 使用正则表达式替换链接为纯文本
    return re.sub(pattern, r'\1', text)