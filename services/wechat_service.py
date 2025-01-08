import json
from llm.llm_factory import LLMFactory
from utils.mem0ai_util import query as mem0ai_query,add as mem0ai_add

def simple_reply(sender_nickname,content):
    system_prompt = """你是一个博学且幽默的人，正在使用wechat聊天工具和人或在群聊中与人聊天，你将得到和你对话的人的简介和他跟你说的话，你会像朋友聊天一样回复他"""
    messages = [
        {"role": "system", "content": system_prompt},
        
    ]
    # 读取记忆
    mem0_msg = mem0ai_query(content,sender_nickname)
    mem0_msg_json = json.dumps(mem0_msg, ensure_ascii=False, indent=2)
    print(f"mem0_msg JSON 格式输出:")
    print(mem0_msg_json)
    if mem0_msg:
        for index, result in enumerate(mem0_msg['results'], start=1):
            if 'memory' in result and result['memory']:
                assistant_msg = {
                    "role": "assistant",
                    "content": f"聊天对象的简介{index}：{result['memory']}"
                }
                messages.append(assistant_msg)
    question = {"role": "user", "content": content}
    messages.append(question)
    llm_service = LLMFactory.get_llm_service("gemini")
    completion = llm_service.get_search_chat_completion(messages)
    eachs = []
    for each in completion.candidates[0].content.parts:
        eachs.append(each.text)
    ai_response = ";".join(eachs)
    mem0_msg = [
        {
            'role':'user',
            'content':content
        },
        {
            'role':'assistant',
            'content':ai_response
        }
    ]
    mem0ai_add(mem0_msg,sender_nickname)
    return ai_response