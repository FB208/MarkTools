import json
import ast
import re

def check_json(json_str: str, schema: str | dict) -> tuple[bool, str]:
    """
    根据模板 JSON 校验目标字符串的格式是否符合要求
    
    Args:
        json_str: 要校验的 JSON 字符串
        schema: 模板 JSON 字符串或字典对象，用于定义预期的数据结构
        
    Returns:
        tuple[bool, str]: (是否验证通过, 错误信息)
        如果验证通过返回 (True, "")，否则返回 (False, 错误原因)
    """
    try:
        # 解析输入的 JSON 字符串
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            return False, f"JSON 解析错误: {str(e)}"
        
        # 处理 schema 参数
        try:
            if isinstance(schema, str):
                schema = json.loads(schema)
            elif not isinstance(schema, dict):
                return False, "schema 必须是 JSON 字符串或字典对象"
        except json.JSONDecodeError as e:
            return False, f"schema 解析错误: {str(e)}"
        
        def check_structure(target, template, path=""):
            # 处理数字类型（int 和 float 可以互换）
            if isinstance(template, (int, float)) and isinstance(target, (int, float)):
                return True, ""
                
            # 检查基本数据类型
            if type(template) != type(target) and not (isinstance(template, (int, float)) and isinstance(target, (int, float))):
                return False, f"路径 '{path}' 的类型不匹配: 期望 {type(template).__name__}, 实际 {type(target).__name__}"
                
            # 如果是列表类型
            if isinstance(template, list):
                if not template:  # 如果模板列表为空，则允许任何列表
                    return True, ""
                if not target:  # 如果目标列表为空，但模板不为空
                    return False, f"路径 '{path}' 的列表为空，但期望有内容"
                    
                # 检查列表中的每个元素是否符合模板中第一个元素的格式
                template_item = template[0]
                for i, item in enumerate(target):
                    is_valid, error = check_structure(item, template_item, f"{path}[{i}]")
                    if not is_valid:
                        return False, error
                return True, ""
                
            # 如果是字典类型
            elif isinstance(template, dict):
                # 检查所有必需的键是否存在，并且值的类型是否正确
                for key in template:
                    if key not in target:
                        return False, f"路径 '{path}' 缺少必需的键 '{key}'"
                    is_valid, error = check_structure(target[key], template[key], f"{path}.{key}")
                    if not is_valid:
                        return False, error
                return True, ""
                
            # 对于其他基本类型，返回 True
            return True, ""
                
        is_valid, error = check_structure(data, schema)
        return is_valid, error if not is_valid else ""
        
    except Exception as e:
        return False, f"未预期的错误: {str(e)}"


def robust_parse_json_like(json_like: str, max_unwrap: int = 2) -> object:
    """
    稳健解析“看起来像 JSON”的字符串。

    功能特性：
    - 去除 ```json ... ``` 或 ``` 包裹的代码块
    - 优先使用 json.loads 解析标准 JSON
    - 失败后使用 ast.literal_eval 兜底，解析 Python 字面量风格（如 {'a': 1}）
    - 若解析结果是字符串（外层再次包裹），最多继续解包 max_unwrap 次

    Args:
        json_like: 可能是 JSON/代码块/字符串字面量/再次包裹的字符串
        max_unwrap: 最大二次解包次数（处理外层再包裹为字符串的情况）

    Returns:
        解析得到的 Python 对象（dict/list/str/数值等）

    Raises:
        ValueError: 无法解析为 JSON/JSON-like 内容
    """
    if json_like is None:
        raise ValueError("json_like 不能为空")

    # 清洗代码块包裹
    content = str(json_like).strip()
    # 去掉以 ```lang 开头的前缀
    content = re.sub(r"^```[a-zA-Z0-9_+\-]*\s*", "", content)
    # 去掉末尾的 ```
    content = re.sub(r"\s*```$", "", content).strip()

    current = content
    attempts = max(1, int(max_unwrap) + 1)
    for _ in range(attempts):
        # 1) 尝试标准 JSON
        try:
            return json.loads(current)
        except json.JSONDecodeError:
            pass

        # 2) 尝试 Python 字面量（如 {'data': ...}）
        try:
            value = ast.literal_eval(current)
        except Exception:
            value = None

        if value is None:
            break

        # 如果得到的是容器类型，直接返回
        if isinstance(value, (dict, list)):
            return value

        # 如果还是字符串，继续解包
        if isinstance(value, str):
            current = value.strip()
            continue

        # 其他基本类型（数值、布尔等）直接返回
        return value

    raise ValueError("Invalid JSON-like content: 解析失败或格式不受支持")