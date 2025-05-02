from llm.llm_factory import LLMFactory
from models.shared_resource import SharedResource
from prompts.general_system_prompt import get_general_system_prompt
from utils.redis_util import RedisUtil
import time
import asyncio
import threading
from flask import current_app

def process_text_content(from_user, content):
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
    elif content and content=="继续":
        redis_util = RedisUtil()
        for _ in range(4):
            # 查询Redis
            result = redis_util.get_value(f"wechat_sub_account_chat:{from_user}")
            if result and result.decode() != 'null':
                redis_util.delete_value(f"wechat_sub_account_chat:{from_user}")
                return result.decode() if isinstance(result, bytes) else result
            elif not result:
                return "没有进行中的任务哦~"
            # 等待1秒
            time.sleep(1)
        return "正在思考，请回复'继续'获取结果"
    else:
        # 在后台线程中执行异步任务，不阻塞主流程
        app = current_app._get_current_object()
        threading.Thread(
            target=lambda: run_bg_chat(app, from_user, content),
            daemon=True
        ).start()
        
        # 循环查询Redis，检查是否有结果
        redis_util = RedisUtil()
        for _ in range(4):
            # 查询Redis
            result = redis_util.get_value(f"wechat_sub_account_chat:{from_user}")
            if result and result.decode() != 'null':
                redis_util.delete_value(f"wechat_sub_account_chat:{from_user}")
                return result.decode() if isinstance(result, bytes) else result
            # 等待1秒
            time.sleep(0.8)
        
        # 4次查询后仍无结果
        return "正在思考，请回复'继续'获取结果"

# 辅助函数：在新线程中运行异步任务
def run_bg_chat(app, from_user, content):
    try:
        # 创建Flask应用上下文
        with app.app_context():
            redis_util = RedisUtil()
            redis_util.set_value_with_expiry(f"wechat_sub_account_chat:{from_user}", 'null', 60*10)
            llm = LLMFactory.get_llm_service("glm")
            response = llm.get_chat_completion([
                {"role": "system", "content": get_general_system_prompt()},
                {"role": "user", "content": content}
            ])
            msg = llm.get_messages(response)
            redis_util.set_value_with_expiry(f"wechat_sub_account_chat:{from_user}", msg, 60*10)
    except Exception as e:
        print(f"后台任务出错: {e}")
    finally:
        # loop.close()
        pass


def process_image_content(content):
    pass
