import json

def convert_to_string(obj):
    try:
        # 尝试将对象解析为 JSON
        json_obj = json.loads(obj)
        # 如果解析成功，将 JSON 对象转换回字符串
        return json.dumps(json_obj, ensure_ascii=False)
    except (TypeError, json.JSONDecodeError):
        # 如果解析失败，说明对象已经是字符串
        return str(obj)