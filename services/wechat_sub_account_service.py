from llm.llm_factory import LLMFactory
from models.shared_resource import SharedResource
def process_text_content(content):
    if content and (content.startswith('k') or content.startswith('K')):
        # 以k/K开头的处理逻辑
        shard_resource = SharedResource.get_by_id(content)
        if shard_resource:
            return_content = f"""
            **{shard_resource.r_name}**
            {shard_resource.r_value}
            """
            return return_content
        else:
            return "没有找到相关记录"
    llm = LLMFactory.get_llm_service("grok")
    response = llm.get_chat_completion([
        {"role": "system", "content": "你是一个语言学专家，擅长文字理解。"},
        {"role": "user", "content": content}
    ])
    return response

def process_image_content(content):
    pass
