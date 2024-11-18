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

# pytest -s tests/utils/vika_util_test.py::test_get_records
def test_get_records():
    with app.app_context():
        vika_client = VikaClient()
        
        # 查询所有数据
        result = vika_client.get_records(
            datasheet_id="dstGf7rE8sHNARigHC",
            pageSize=100  # 每页返回100条记录
        )
        
        print(result)
        # 验证API调用是否成功
        assert result['success'] == True
        
        # 打印记录总数
        total = result['data']['total']
        print(f"\n总记录数: {total}")
        
        # 打印每条记录的内容
        records = result['data']['records']
        for record in records:
            print("\n记录ID:", record['recordId'])
            print("字段内容:", record['fields'])

