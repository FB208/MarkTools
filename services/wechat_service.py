
from llm.llm_factory import LLMFactory

def simple_reply(content):
    system_prompt = """你是一个拟人化的问答机器人，基于别人跟你说的话，给出人性化的回复"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]
    llm_service = LLMFactory.get_llm_service()
    completion = llm_service.get_chat_completion(messages)
    return llm_service.get_messages(completion)