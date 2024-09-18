import os
import json
import google.auth
from google.auth.transport.requests import Request
import google.generativeai as genai

def list():
    # 使用服务账号 JSON 文件进行身份验证
    json_file_path = os.path.join('google_credentials', 'meta-buckeye-433400-c6-109fbeae7021.json')
    # try:
    #     with open(json_file_path, 'r', encoding='utf-8') as file:
    #         credentials_info = json.load(file)
    #     print(credentials_info)  # 这行打印出了 JSON 内容，说明文件读取成功
    # except FileNotFoundError:
    #     print(f"错误：找不到文件 {json_file_path}")
    #     return []
    # except json.JSONDecodeError:
    #     print(f"错误：无法解析 JSON 文件 {json_file_path}")
    #     return []

    # 加载凭据
    credentials, _ = google.auth.load_credentials_from_file(json_file_path)

    # 如果凭据需要刷新，刷新它
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    # 配置 genai 使用这些凭据
    genai.configure(credentials=credentials)

    # 现在您可以使用 API 了
    
    
    training_data = [
        {"text_input": "1", "output": "2"},
        {"text_input": "3", "output": "4"},
        {"text_input": "-3", "output": "-2"},
        {"text_input": "twenty two", "output": "twenty three"},
        {"text_input": "two hundred", "output": "two hundred one"},
        {"text_input": "ninety nine", "output": "one hundred"},
        {"text_input": "8", "output": "9"},
        {"text_input": "-98", "output": "-97"},
        {"text_input": "1,000", "output": "1,001"},
        {"text_input": "10,100,000", "output": "10,100,001"},
        {"text_input": "thirteen", "output": "fourteen"},
        {"text_input": "eighty", "output": "eighty one"},
        {"text_input": "one", "output": "two"},
        {"text_input": "three", "output": "four"},
        {"text_input": "seven", "output": "eight"},
    ]
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("介绍一下你自己")
    print(response.text)    
    try:
        print('调优模型')
        for model_info in genai.list_tuned_models():
            print(model_info.name)
    except Exception as e:
        print(f"列出调优模型时出错：{str(e)}")
        
    model = genai.GenerativeModel(model_name="tunedModels/intadd1-2t90cts7dd8s")
    result = model.generate_content("123")
    print(result.text)  # "IV"

    return '123'