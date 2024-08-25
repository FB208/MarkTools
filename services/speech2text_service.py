import requests
import json
import os
import uuid
import base64
from werkzeug.utils import secure_filename
from flask import current_app as app
from utils.openai_whisper_util import transcribe_audio
from llm.llm_factory import LLMFactory

def get_text(file):
    file_extension = os.path.splitext(file.filename)[1]
    temp_file_name = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join('tempfiles', secure_filename(temp_file_name))
    file.save(file_path)
    # 确保文件句柄已关闭
    file.close()
    try:
        text = transcribe_audio(file_path)
    except Exception as e:
        print(e)
        text = ""
    finally:
        os.remove(file_path)
    
    # 优化识别结果
    system_prompt = """你是专业的音频转录专家，你的任务是检查收到的文本，修正其中的错误。
    你收到的内容是由工具通过人类录音识别出来的文本。
    你需要注意以下几点：
    1. 人声朗读可能出现错字、漏字、口吃等问题。
    2. 人说话时如果说错了，可能会重复一遍之前的话以保证正确，这种情况你需要把前面那段错误的话擅长。
    3. 语音识别工具也可能出现识别不准确的情况。
    4. 文本以中文为主，但可能夹杂英文单词，所以遇到不明白的词语，尝试同音的英文看是否能组成完整的意思。
    不要用任何文字修饰，直接输出修正后的文本"""
    
    messages = [
        {"role": "system", "content": f"{system_prompt}"},
        {"role": "user", "content": f"{text}"}
    ]
    llm_service = LLMFactory.get_llm_service()
    completion = llm_service.get_chat_completion(messages)
    result_text = llm_service.get_messages(completion)
    print(result_text)
    return result_text