import json
import time
from llm.llm_factory import LLMFactory
from utils.mem0ai_util import query as mem0ai_query,add as mem0ai_add
from models.wechat_user import WechatUser
from utils.redis_util import RedisUtil
import threading
from flask import current_app

def summary_thread(msg_type, chat_key, sender_nickname, app):
    """异步处理聊天摘要
    
    Args:
        msg_type: 消息类型
        chat_key: 聊天主键
        sender_nickname: 发送者昵称
        app: Flask应用实例
    """
    with app.app_context():  # 创建应用上下文
        try:
            # 创建Redis工具类实例
            redis_util = RedisUtil()
            
            # 获取消息总数
            msg_count = redis_util.get_chat_history_count(msg_type, chat_key)
            
            if msg_count > 5:
                # 获取并删除旧消息（保留最近3条）
                old_messages = redis_util.get_chat_history_except_recent(msg_type, chat_key, keep_recent=3)
                
                # 获取用户当前的性格摘要
                user = WechatUser.get_by_nickname(sender_nickname)
                if user and user[0]:
                    current_summary = user[0].personality_summary
                    
                    system_message = """你是一个擅长总结聊天记录的人，擅长根据聊天记录总结出关键事件、人物关系和性格特点
                    你将收到三组内容：
                    1. 之前总结的摘要，用<OLD_SUMMARY>标签包裹
                    2. 最近的聊天记录，用<NEW_CHAT_RECORD>标签包裹
                    3. 之前总结的用户画像，用<BASE_INFO>标签包裹

                    你将要输出一个json对象，格式如下：
                    {
                        "摘要": "你新总结的摘要内容",
                        "人物画像": {
                            "姓名/昵称": "彭于晏",
                            "性别": "男",
                            "地址": "天津河东",
                            "简介": "性格乐观，爱聊天，经济情况不错，喜欢文学"
                        }
                    } 
                    要求：
                    1. 你将根据这两组内容，生成新的摘要和人物画像。
                    2. 新的摘要应该包含之前总结的摘要和最近的聊天记录。
                    3. 新的摘要应该简洁明了，不需要华丽的修饰，突出重点，不要超过500字。
                    4. 人物画像要确保准确再更新。
                    5. 直接返回我要求的json对象，不要提供任何解释或文本。
                    
                    """
                    user_prompt = f"""
                    之前总结的摘要：<OLD_SUMMARY>{current_summary}</OLD_SUMMARY>
                    最近的聊天记录：<NEW_CHAT_RECORD>{old_messages}</NEW_CHAT_RECORD>
                    之前总结的用户画像：<BASE_INFO>{user[0].base_info}</BASE_INFO>
                    """
                    messages = [
                        {"role": "system", "content": f"{system_message}"},
                        {"role": "user", "content": f"{user_prompt}"}
                    ]
                    llm_service = LLMFactory.get_llm_service("deepseek")
                    completion = llm_service.get_json_completion(messages)
                    json_data = llm_service.get_messages(completion)
                    print("json_data",json_data)
                    # 解析 JSON 字符串为 Python 字典
                    if isinstance(json_data, str):
                        json_data = json.loads(json_data)
                    
                    base_info = json_data.get('人物画像')
                    personality_summary = json_data.get('摘要')
                    print("base_info",base_info)
                    print("personality_summary",personality_summary)
                    user[0].base_info = base_info
                    user[0].personality_summary = personality_summary
                    user[0].save()
        except Exception as e:
            print(f"摘要处理发生错误: {str(e)}")
            # 这里可以添加错误日志记录
        
def create_summary_thread(msg_type, chat_key, sender_nickname):
    """创建并启动摘要处理线程
    
    Args:
        msg_type: 消息类型
        chat_key: 聊天主键
        sender_nickname: 发送者昵称
    """
    app = current_app._get_current_object()  # 获取真实的应用实例
    thread = threading.Thread(
        target=summary_thread,
        args=(msg_type, chat_key, sender_nickname, app),
        daemon=False  # 设置为非守护线程
    )
    thread.start()
    return thread

def simple_reply(type="single_user",chat_primary_key='',sender_nickname='',content=''):
    '''
    type: 聊天类型，single_user: 单聊，chat_room: 群聊
    chat_primary_key: 聊天主键，单聊时为发送者昵称，群聊时为群名
    sender_nickname: 发送者昵称
    content: 发送者发送的内容
    '''
    try:
        # 创建Redis工具类实例
        redis_util = RedisUtil()
        
        system_prompt = """你叫mark，是一个博学且幽默的人，正在使用wechat聊天工具和人或在群聊中与人聊天，你会像朋友聊天一样回复他。
        在消息中，你会收到三部分内容（如果你没有收到简介或摘要，则说明你们是初次聊天）：
        1. 聊天对象的简介：有助于你了解聊天对象，不必每次都提及
        2. 之前聊天的摘要：有助于你进一步了解你和聊天对象之间的关系，但也只是参考，不必每次都提及
        3. 近期聊天的几条记录：你需要结合这些记录来给出上下文连贯的回复，就像真的聊天一样
        
        回复要求：
        1. 风趣幽默，平易近人
        2. 不懂的内容从网上搜索，不要乱编
        3. 从网上搜到的内容要说清楚来源于网络
        4. 实在无法回答的可以说不知道，不要胡编乱造
        5. 不要使用markdown格式，将回复内容组织成一段话，就像人类聊天一样
        """
        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # 获取用户信息
        user = WechatUser.get_by_nickname(sender_nickname)
        if user:
            assistant_msg = {
                "role": "assistant",
                "content": f"聊天对象的简介：{user[0].base_info}"
            }
            messages.append(assistant_msg)
            if user[0].personality_summary:
                assistant_msg = {
                    "role": "assistant",
                    "content": f"之前聊天的摘要：{user[0].personality_summary}"
                }
                messages.append(assistant_msg)
        
        # 获取最近的聊天记录
        recent_messages = redis_util.get_recent_chat_history(type, chat_primary_key)
        if recent_messages:
            for msg_data in recent_messages:
                messages.extend(msg_data['msg'])
        
        # 添加当前问题
        question = {"role": "user", "content": content}
        messages.append(question)
        print("发送的消息集合：")
        print(messages)
        print("--------------------------------")
        # 获取AI回复
        llm_service = LLMFactory.get_llm_service("gemini")
        completion = llm_service.get_search_chat_completion(messages)
        print("completion",completion)
        eachs = []
        for each in completion.candidates[0].content.parts:
            eachs.append(each.text)
        ai_response = ";".join(eachs)
        
        # 构建并保存本次对话历史
        history_msg = [
            {
                'role':'user',
                'content':content
            },
            {
                'role':'assistant',
                'content':ai_response
            }
        ]
        redis_util.save_chat_history(type, chat_primary_key, history_msg)
        
        # 异步启动摘要处理（使用非守护线程）
        create_summary_thread(type, chat_primary_key, sender_nickname)
        
        return ai_response
    except Exception as e:
        print(f"simple_reply发生错误: {str(e)}")
        return "我累了，让我歇一会儿吧"

