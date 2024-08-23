import pytest
import json
from utils.coze_api_util import conversation_create, chat, message_create
from run import create_app
from test_config import TestConfig

# 创建Flask应用
app = create_app()
app.config.from_object(TestConfig)

def test_conversation_create():
    with app.app_context():
        result = conversation_create()
        print(result)
        assert False
        
def test_chat():
    with app.app_context():
        result = conversation_create()
        print(result)
        conversation_id = result['data']['id']
        content = [{"type":"text","text":"转文字"},{"type":"file","file_url":"https://123.markup.com.cn/ibed/202408121555213.mp3"}]
        serialized_data = json.dumps(content, ensure_ascii=False)
        result = chat(conversation_id, "7402121382764888073", serialized_data)
        print(result)
        assert False
        
def test_message_create():
    with app.app_context():
        result = conversation_create()
        print(result)
        conversation_id = result['data']['id']
        result = message_create(conversation_id, "介绍一下你自己")
        print(result)
        assert False