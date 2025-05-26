# Gemini 2.0 API 使用指南

## 概述

Gemini 2.0 API 与之前版本的 API 格式有所不同。最主要的变化是消息格式的结构变化，特别是 `contents` 字段的格式。本文档提供了如何正确使用 Gemini 2.0 API 的指南。

## 主要变化

1. 消息格式变化：每个消息必须包含 `role` 和 `parts` 结构。
2. API 库变更：使用最新的 `google-genai` 库（版本 1.16.1 及以上）。

## 正确的消息格式

```python
contents = [
    {
        "role": "user",  # 或 "model"
        "parts": [{"text": "消息内容"}]
    },
    # 更多消息...
]
```

## 示例用法

### 基本聊天完成

```python
from llm.gemini_llm_service import GeminiLLMService

messages = [
    {"role": "system", "content": "你是一个全能助手，善于回答用户提出的问题"},
    {"role": "user", "content": "讲个故事吧"}
]

llm_service = GeminiLLMService()
completion = llm_service.get_chat_completion(messages, model="gemini-2.0-flash-exp")
result = llm_service.get_messages(completion)
print(result)
```

### 使用搜索功能

```python
from llm.gemini_llm_service import GeminiLLMService

messages = [
    {"role": "system", "content": "你是一个全能助手，善于回答用户提出的问题"},
    {"role": "user", "content": "今天天气如何？"},
    {"role": "assistant", "content": "你在哪个城市呢？"},
    {"role": "user", "content": "我在杭州"}
]

llm_service = GeminiLLMService()
completion = llm_service.get_search_chat_completion(messages, model="gemini-2.0-flash-exp")
print(completion)
```

### JSON 格式响应

```python
from llm.gemini_llm_service import GeminiLLMService

messages = [
    {"role": "system", "content": "你是一个全能助手，善于回答用户提出的问题，请以JSON格式返回响应"},
    {"role": "user", "content": "给我三本经典小说的推荐"}
]

llm_service = GeminiLLMService()
completion = llm_service.get_json_completion(messages, model="gemini-2.0-flash")
print(completion)
```

## 常见错误

1. **验证错误**：通常是由于消息格式不正确，确保每个消息包含正确的 `role` 和 `parts` 结构。
2. **模型兼容性问题**：确保使用 Gemini 2.0 兼容的模型名称。

## 调试

如果遇到错误，服务会打印以下调试信息：

1. 错误消息
2. 错误堆栈跟踪
3. 发送到 API 的请求内容

这些信息可以帮助识别和解决问题。

## 注意事项

- 不同于 OpenAI API，Gemini API 的角色分为 "user" 和 "model"（不是 "assistant"）。
- system 指令会被单独提取和处理，不包含在 contents 中。 