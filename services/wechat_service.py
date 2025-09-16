import json
import time
from llm.llm_factory import LLMFactory
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
                    
                    system_message = f"""你是一个擅长总结聊天记录的人，擅长根据聊天记录总结出关键事件、人物关系和性格特点
                    你将收到两组内容：
                    1. 之前总结的摘要，用<OLD_SUMMARY>标签包裹
                    2. 最近的聊天记录，用<NEW_CHAT_RECORD>标签包裹
                    
                    要求：
                    1. 你将根据这两组内容，生成新的摘要。
                    2. 新的摘要应该包含之前总结的摘要和最近的聊天记录，但不要重复之前的摘要。
                    3. 新的摘要应该简洁明了，不要超过300字。
                    4. 直接返回新的摘要，不要提供任何解释或文本。
                    """
                    user_prompt = f"""
                    之前总结的摘要：<OLD_SUMMARY>{current_summary}</OLD_SUMMARY>
                    最近的聊天记录：<NEW_CHAT_RECORD>{old_messages}</NEW_CHAT_RECORD>
                    """
                    messages = [
                        {"role": "system", "content": f"{system_message}"},
                        {"role": "user", "content": f"{user_prompt}"}
                    ]
                    llm_service = LLMFactory.get_llm_service("deepseek")
                    completion = llm_service.get_chat_completion(messages)
                    new_summary = llm_service.get_messages(completion)
                    print("new_summary",new_summary)
                    user[0].personality_summary = new_summary
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

