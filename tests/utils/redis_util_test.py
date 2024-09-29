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

