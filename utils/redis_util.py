import redis
import json
import time
from flask import current_app as app

class RedisUtil:
    def __init__(self):
        self.client = redis.StrictRedis.from_url(
            app.config['REDIS_URL']
        )

    def set_value(self, key, value):
        """设置键值对"""
        self.client.set(key, value)

    def get_value(self, key):
        """获取键的值"""
        return self.client.get(key)

    def delete_value(self, key):
        """删除键值对"""
        self.client.delete(key)

    def update_value(self, key, value):
        """更新键值对"""
        self.set_value(key, value)

    def publish_message(self, channel, message):
        """发布消息到指定频道"""
        self.client.publish(channel, message)

    def listen(self, channel, message_handler):
        """持续监听订阅的频道并处理收到的消息"""
        pubsub = self.client.pubsub()
        pubsub.subscribe(channel)
        for message in pubsub.listen():
            if message['type'] == 'message':
                message_handler(message['data'])

    def save_chat_history(self, msg_type, chat_key, history_msg, max_history=100):
        """保存聊天历史
        
        Args:
            msg_type: 消息类型（single_user/chat_room）
            chat_key: 聊天主键（单聊为用户昵称，群聊为群名）
            history_msg: 历史消息内容
            max_history: 最大保留的历史消息数量
        """
        timestamp = int(time.time())
        content = {
            "msg": history_msg,
            "timestamp": timestamp
        }
        
        key = f"chat_history:{msg_type}:{chat_key}"
        # 添加新消息
        self.client.zadd(key, {json.dumps(content): timestamp})
        
        # 只保留最新的消息
        self.client.zremrangebyrank(key, 0, -(max_history + 1))
        
    def get_recent_chat_history(self, msg_type, chat_key, count=3):
        """获取最近的聊天历史
        
        Args:
            msg_type: 消息类型（single_user/chat_room）
            chat_key: 聊天主键（单聊为用户昵称，群聊为群名）
            count: 获取的消息数量
            
        Returns:
            最近的count条消息，按时间从新到旧排序
        """
        key = f"chat_history:{msg_type}:{chat_key}"
        messages = self.client.zrevrangebyscore(
            key,
            max=float('inf'),
            min=float('-inf'),
            start=0,
            num=count
        )
        
        return [json.loads(msg.decode()) for msg in messages] if messages else []

    def clear_chat_history(self, msg_type, chat_key):
        """清除聊天历史
        
        Args:
            msg_type: 消息类型（single_user/chat_room）
            chat_key: 聊天主键（单聊为用户昵称，群聊为群名）
        """
        key = f"chat_history:{msg_type}:{chat_key}"
        self.client.delete(key)

    def get_chat_history_count(self, msg_type, chat_key):
        """获取聊天历史消息数量
        
        Args:
            msg_type: 消息类型（single_user/chat_room）
            chat_key: 聊天主键（单聊为用户昵称，群聊为群名）
            
        Returns:
            消息数量
        """
        key = f"chat_history:{msg_type}:{chat_key}"
        return self.client.zcard(key)

    def get_chat_history_except_recent(self, msg_type, chat_key, keep_recent=3):
        """获取除了最近n条之外的所有历史消息
        
        Args:
            msg_type: 消息类型（single_user/chat_room）
            chat_key: 聊天主键（单聊为用户昵称，群聊为群名）
            keep_recent: 保留最近的消息数量
            
        Returns:
            历史消息列表，按时间从新到旧排序
        """
        key = f"chat_history:{msg_type}:{chat_key}"
        total = self.client.zcard(key)
        if total <= keep_recent:
            return []
            
        messages = self.client.zrevrange(
            key,
            keep_recent,  # 跳过最近的keep_recent条
            -1  # 直到最后一条
        )
        
        # 删除这些消息
        self.client.zremrangebyrank(key, 0, total - keep_recent - 1)
        
        return [json.loads(msg.decode()) for msg in messages] if messages else []

