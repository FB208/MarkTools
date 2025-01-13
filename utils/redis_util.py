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
        
        key = f"starbot:chat_history:{msg_type}:{chat_key}"
        # 添加新消息，确保中文正常存储
        self.client.zadd(key, {json.dumps(content, ensure_ascii=False): timestamp})
        
        # 只保留最新的消息
        self.client.zremrangebyrank(key, 0, -(max_history + 1))
        
    def get_recent_chat_history(self, msg_type, chat_key, count=3):
        """获取最近的聊天历史
        
        Args:
            msg_type: 消息类型（single_user/chat_room）
            chat_key: 聊天主键（单聊为用户昵称，群聊为群名）
            count: 获取的消息数量
            
        Returns:
            最近的count条消息，按时间从旧到新排序
        """
        key = f"starbot:chat_history:{msg_type}:{chat_key}"
        messages = self.client.zrevrangebyscore(
            key,
            max=float('inf'),
            min=float('-inf'),
            start=0,
            num=count
        )
        
        # 解析消息并反转顺序，使其从旧到新排序
        history = [json.loads(msg.decode('utf-8')) for msg in messages] if messages else []
        return list(reversed(history))

    def clear_chat_history(self, msg_type, chat_key):
        """清除聊天历史
        
        Args:
            msg_type: 消息类型（single_user/chat_room）
            chat_key: 聊天主键（单聊为用户昵称，群聊为群名）
        """
        key = f"starbot:chat_history:{msg_type}:{chat_key}"
        self.client.delete(key)

    def get_chat_history_count(self, msg_type, chat_key):
        """获取聊天历史消息数量
        
        Args:
            msg_type: 消息类型（single_user/chat_room）
            chat_key: 聊天主键（单聊为用户昵称，群聊为群名）
            
        Returns:
            消息数量
        """
        key = f"starbot:chat_history:{msg_type}:{chat_key}"
        return self.client.zcard(key)

    def get_chat_history_except_recent(self, msg_type, chat_key, keep_recent=3):
        """获取除了最近n条之外的所有历史消息
        
        Args:
            msg_type: 消息类型（single_user/chat_room）
            chat_key: 聊天主键（单聊为用户昵称，群聊为群名）
            keep_recent: 保留最近的消息数量
            
        Returns:
            历史消息列表，按时间从旧到新排序
        """
        key = f"starbot:chat_history:{msg_type}:{chat_key}"
        total = self.client.zcard(key)
        if total <= keep_recent:
            return []
            
        messages = self.client.zrange(
            key,
            0,  # 从最早的消息开始
            total - keep_recent - 1  # 到倒数第keep_recent条之前
        )
        
        # 删除这些旧消息
        #self.client.zremrangebyrank(key, 0, total - keep_recent - 1)
        
        return [json.loads(msg.decode('utf-8')) for msg in messages] if messages else []

    def array_push(self, key, *values):
        """向数组中添加一个或多个元素
        
        Args:
            key: 数组的键名
            values: 要添加的一个或多个值
        
        Returns:
            添加后数组的长度
        """
        # 将字典类型转换为JSON字符串，确保中文正常显示
        processed_values = [json.dumps(v, ensure_ascii=False) if isinstance(v, dict) else v for v in values]
        return self.client.rpush(key, *processed_values)

    def array_get_all(self, key):
        """获取数组中的所有元素
        
        Args:
            key: 数组的键名
            
        Returns:
            数组中的所有元素列表
        """
        values = self.client.lrange(key, 0, -1)
        result = []
        for value in values:
            if isinstance(value, bytes):
                value = value.decode()
            try:
                # 尝试解析JSON
                result.append(json.loads(value))
            except (json.JSONDecodeError, TypeError):
                result.append(value)
        return result

    def array_remove(self, key, value, count=0):
        """从数组中删除指定的元素
        
        Args:
            key: 数组的键名
            value: 要删除的值
            count: 要删除的数量。
                  count > 0: 从头到尾删除count个
                  count < 0: 从尾到头删除count个
                  count = 0: 删除所有匹配的元素
        
        Returns:
            被删除的元素数量
        """
        return self.client.lrem(key, count, value)

    def array_length(self, key):
        """获取数组的长度
        
        Args:
            key: 数组的键名
            
        Returns:
            数组的长度
        """
        return self.client.llen(key)

    def array_pop(self, key):
        """弹出数组最后一个元素
        
        Args:
            key: 数组的键名
            
        Returns:
            弹出的元素，如果数组为空则返回None
        """
        value = self.client.rpop(key)
        return value.decode() if isinstance(value, bytes) else value

    def array_clear(self, key):
        """清空数组
        
        Args:
            key: 数组的键名
        """
        self.delete_value(key)

    def array_add_or_replace(self, key, values):
        """替换数组的所有内容
        
        Args:
            key: 数组的键名
            values: 新的数组内容，可以是列表、元组或任何可迭代对象
            
        Returns:
            新数组的长度
        """
        # 将字典类型转换为JSON字符串，确保中文正常显示
        processed_values = [json.dumps(v, ensure_ascii=False) if isinstance(v, dict) else v for v in values]
        pipeline = self.client.pipeline()
        pipeline.delete(key)
        if processed_values:  # 只有在有新值的情况下才执行rpush
            pipeline.rpush(key, *processed_values)
        results = pipeline.execute()
        return results[-1] if processed_values else 0

    def delete_by_pattern_scan(self, pattern):
        """使用scan命令根据模式删除匹配的所有键（生产环境推荐）
        
        Args:
            pattern: 键名匹配模式，例如 'starbot:robot_info:*'
            
        Returns:
            删除的键的数量
        """
        deleted_count = 0
        cursor = '0'
        while cursor != 0:
            cursor, keys = self.client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                deleted_count += self.client.delete(*keys)
        return deleted_count

    def set_json(self, key, value):
        """将 Python 对象（如字典）序列化为 JSON 字符串并存储
        
        Args:
            key: 键名
            value: Python 对象（通常是字典或列表）
        """
        json_str = json.dumps(value, ensure_ascii=False)
        self.client.set(key, json_str)

    def get_json(self, key):
        """获取并反序列化存储的 JSON 字符串为 Python 对象
        
        Args:
            key: 键名
            
        Returns:
            Python 对象（通常是字典或列表），如果键不存在则返回 None
        """
        value = self.client.get(key)
        if value is None:
            return None
        return json.loads(value)

