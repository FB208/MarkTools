import pytest
from app import create_app
from test_config import TestConfig
from utils.vika_util import VikaClient
# 创建Flask应用
app = create_app()
app.config.from_object(TestConfig)

# pytest -s tests/utils/vika_util_test.py::test_create_vika_datasheet
def test_create_vika_datasheet():
    with app.app_context():
        vika_client = VikaClient()
        name = "表格标题"
        description = "表格描述"
        fields = [
            {
                "type": "Text",
                "name": "标题"
            }
        ]
        try:
            result = vika_client.create_datasheet(name, description, fields=fields)
            print(result)
        except Exception as e:
            print(f"Error: {e}")
