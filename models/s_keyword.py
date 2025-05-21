from peewee import *
from .base_model import BaseModel

class SKeyword(BaseModel):
    """系统设置表"""
    id = AutoField(primary_key=True)
    key_type = CharField(max_length=50, null=True, help_text='组类型、名称')
    key_code = CharField(max_length=100, null=True, help_text='key')
    key_content = TextField(null=True, help_text='value')
    sort = FloatField(null=True, help_text='排序')
    enable = IntegerField(null=True, help_text='启用状态')
    memo = CharField(max_length=255, null=True, help_text='说明')
    
    class Meta:
        table_name = 's_keyword'
        
    @classmethod
    def get_by_type_code(cls, key_type, key_code):
        """
        根据类型和代码查询关键字记录
        
        Args:
            key_type: 关键字类型
            key_code: 关键字代码
            
        Returns:
            查询到的关键字记录，如果未找到则返回None
        """
        try:
            return cls.get((cls.key_type == key_type) & (cls.key_code == key_code) & (cls.enable == 1))
        except cls.DoesNotExist:
            return None