# Gemini 2.0 API接口实现
# 注意：该接口与Gemini 1.5及之前版本不兼容
# Gemini 2.0 API要求使用特定的消息格式，每条消息必须包含role和parts结构
from google import genai as genai
from google.genai import types
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch, Part
from flask import current_app as app
from .llm_interface import LLMInterface
import json
import re
import traceback
from utils.text_util import convert_to_string

class GeminiLLMService(LLMInterface):
    def get_client(self):
        # 获取配置变量
        api_key = app.config['SIMPLE_GOOGLE_API_KEY']
        client = genai.Client(api_key=api_key)
        return client

    def get_messages(self, response):
        print(response)
        return response.text
    def clear_thinking_msg(self, response):
        msg = response.text
        clear_msg = re.sub(r'<think>[\s\S]*?</think>', '', msg)
        return clear_msg
    def _process_openai_messages(self, messages):
        """
        处理OpenAI格式的消息，转换为Gemini 2.0 API格式
        """
        if messages[-1]["role"] != "user":
            raise ValueError("最后一条消息必须是用户消息")
        
        # 提取系统指令
        system_instruction = "You are a helpful assistant."
        
        # 转换为Gemini API格式
        contents = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = convert_to_string(msg["content"])
            else:
                # Gemini API 使用 "user" 和 "model" 作为角色
                role = "model" if msg["role"] == "assistant" else msg["role"]
                content = convert_to_string(msg["content"])
                
                # 创建符合Gemini 2.0格式的消息
                contents.append({
                    "role": role,
                    "parts": [{"text": content}]
                })
        
        return system_instruction, contents

    def get_chat_completion(self, messages,model:str="gemini-2.0-flash-exp"):
        client = self.get_client()
        
        try:
            system_instruction, contents = self._process_openai_messages(messages)
            
            # 创建配置对象
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                thinking_config=types.ThinkingConfig(
                    include_thoughts=True
                )
            )
                
            response = client.models.generate_content(
                    model=model,
                    config=config,
                    contents=contents
                )

            return response
        except Exception as e:
            print(f"Gemini API 错误: {str(e)}")
            print(f"错误详情: {traceback.format_exc()}")
            print(f"请求内容: {json.dumps({'model': model, 'system_instruction': system_instruction, 'contents': contents}, ensure_ascii=False, indent=2)}")
            raise
    
    def get_chat_completion_async(self, messages):
        pass
    def get_chat_completion_async_result(self, task_id):
        pass

    def get_json_completion(self, messages,model:str="gemini-2.0-flash"):
        client = self.get_client()
        
        try:
            system_instruction, contents = self._process_openai_messages(messages)
            
            config = {
                'response_mime_type': 'application/json',
                'system_instruction': system_instruction
            }
            
            response = client.models.generate_content(
                    model=model,
                    config=config,
                    contents=contents)
            
            return response
        except Exception as e:
            print(f"Gemini API JSON格式错误: {str(e)}")
            print(f"错误详情: {traceback.format_exc()}")
            print(f"请求内容: {json.dumps({'model': model, 'system_instruction': system_instruction, 'contents': contents}, ensure_ascii=False, indent=2)}")
            raise
    
    def get_json_completion_v2(self, messages,response_format):
        pass
    
    def get_search_chat_completion(self, messages,model:str="gemini-2.0-flash-exp"):
        '''
        gemini2.0使用最新的google-genai库，和gemini1.5的库不兼容
        '''
        try:
            # 转换消息格式
            system_instruction, contents = self._process_openai_messages(messages)
            client = genai.Client(http_options={'api_version': 'v1alpha'},api_key=app.config['SIMPLE_GOOGLE_API_KEY'])

            google_search_tool = Tool(
                google_search = GoogleSearch()
            )
            
            # 将 system_instruction 转换为列表格式（如果需要）
            system_instructions = [system_instruction] if isinstance(system_instruction, str) else system_instruction
            
            config = GenerateContentConfig(
                system_instruction=system_instructions,
                tools=[google_search_tool],
                response_modalities=["TEXT"]
            )
            
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
            return response
        except Exception as e:
            print(f"Gemini API 搜索功能错误: {str(e)}")
            print(f"错误详情: {traceback.format_exc()}")
            print(f"请求内容: {json.dumps({'model': model, 'system_instruction': system_instruction, 'contents': contents}, ensure_ascii=False, indent=2)}")
            raise
