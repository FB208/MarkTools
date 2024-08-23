import pytest
from utils.coze_api_util import create_conversation
from run import create_app
from test_config import TestConfig

# 创建Flask应用
app = create_app()
app.config.from_object(TestConfig)

def test_create_conversation():
    with app.app_context():
        result = create_conversation()
        print(result)
        assert False