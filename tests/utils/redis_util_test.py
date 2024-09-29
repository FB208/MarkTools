import pytest
from app import create_app
from test_config import TestConfig
from utils.redis_util import RedisUtil
from unittest.mock import patch, MagicMock

# 创建Flask应用
app = create_app()
app.config.from_object(TestConfig)

# pytest -s tests/utils/redis_util_test.py::test_set_value
def test_set_value():
    with app.app_context():
        redis_util = RedisUtil()
        redis_util.set_value('test_key', 'test_value')

# pytest -s tests/utils/redis_util_test.py::test_publish_message
def test_publish_message():
    with app.app_context():
        redis_util = RedisUtil()
        redis_util.publish_message('wechat_cmd', '{"nickname": "杨惠超", "msg": "msg", "type": "friend"}')
        # redis_util.publish_message('wechat_cmd', '{"nickname": "峻峰的人工智能物联网研发事业部", "msg": "呜啦啦", "type": "group"}')

# pytest -s tests/utils/redis_util_test.py::test_listen
def test_listen():
    with app.app_context():
        def message_handler(data):
            print(f"Received message: {data}")
        redis_util = RedisUtil()
        redis_util.listen('wechat_cmd', message_handler)

