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

