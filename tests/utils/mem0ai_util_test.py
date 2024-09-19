import pytest
from utils.mem0ai_util import list_user
from app import create_app
from test_config import TestConfig

# 创建Flask应用
app = create_app()
app.config.from_object(TestConfig)

def test_list_user():
    with app.app_context():
        result = list_user()
        print(result)
        
        # 检查返回值是否为列表
        assert isinstance(result, list), "返回值应该是一个列表"
        
        # 如果列表不为空,检查每个用户是否有预期的字段
        if result:
            for user in result:
                assert 'id' in user, "每个用户应该有 'id' 字段"
                assert 'created_at' in user, "每个用户应该有 'created_at' 字段"
                assert 'updated_at' in user, "每个用户应该有 'updated_at' 字段"
        
        # 添加更多具体的断言,根据您的实际需求来验证返回的用户列表
        
        # 注意: 这个断言总是会失败,用于确保您查看了测试输出
        assert False, "请检查打印的结果并相应地调整测试"