import pytest
from unittest.mock import patch, MagicMock
from services.wechat_service import simple_reply
from app import create_app
from test_config import TestConfig

app = create_app()
app.config.from_object(TestConfig)


@pytest.fixture
def mock_llm_service():
    mock_service = MagicMock()
    mock_completion = MagicMock()
    mock_candidate = MagicMock()
    mock_content = MagicMock()
    mock_part = MagicMock()
    
    mock_part.text = "这是一个测试回复"
    mock_content.parts = [mock_part]
    mock_candidate.content = mock_content
    mock_completion.candidates = [mock_candidate]
    mock_service.get_search_chat_completion.return_value = mock_completion
    return mock_service

@pytest.fixture
def mock_mem0ai_query():
    return {
        "results": [
            {
                "memory": "这是一个测试用户的记忆"
            }
        ]
    }

def test_simple_reply_basic(mock_llm_service):
    with patch('services.wechat_service.LLMFactory.get_llm_service', return_value=mock_llm_service), \
         patch('services.wechat_service.mem0ai_query', return_value={"results": []}), \
         patch('services.wechat_service.mem0ai_add') as mock_mem0ai_add:
        
        result = simple_reply("测试用户", "你好")
        
        assert result == "这是一个测试回复"
        mock_llm_service.get_search_chat_completion.assert_called_once()
        mock_mem0ai_add.assert_called_once()

def test_simple_reply_with_memory(mock_llm_service):
    with patch('services.wechat_service.LLMFactory.get_llm_service', return_value=mock_llm_service), \
         patch('services.wechat_service.mem0ai_query', return_value={"results": [{"memory": "这是一个测试用户的记忆"}]}), \
         patch('services.wechat_service.mem0ai_add') as mock_mem0ai_add:
        
        result = simple_reply("测试用户", "你好")
        
        assert result == "这是一个测试回复"
        # 验证调用LLM时包含了记忆信息
        called_messages = mock_llm_service.get_search_chat_completion.call_args[0][0]
        assert any("这是一个测试用户的记忆" in msg["content"] for msg in called_messages)
        mock_mem0ai_add.assert_called_once()

def test_simple_reply_error_handling():
    with patch('services.wechat_service.LLMFactory.get_llm_service', side_effect=Exception("测试异常")), \
         patch('services.wechat_service.mem0ai_query', return_value={"results": []}):
        
        with pytest.raises(Exception) as exc_info:
            simple_reply("测试用户", "你好")
        
        assert str(exc_info.value) == "测试异常" 