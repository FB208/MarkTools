import redis
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