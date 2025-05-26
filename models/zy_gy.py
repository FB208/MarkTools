from peewee import *
from .base_model import BaseModel

class ZyGy(BaseModel):
    """卦爻信息表"""
    id = CharField(max_length=50, primary_key=True)
    p_id = CharField(max_length=50, null=True, help_text='父ID')
    gy_name = CharField(max_length=50, null=True, help_text='卦名或爻名')
    gy_content = CharField(max_length=255, null=True, help_text='卦辞或爻辞')
    gy_translate = CharField(max_length=500, null=True, help_text='卦象或爻象')
    fate = CharField(max_length=500, null=True, help_text='时运')
    wealth = CharField(max_length=500, null=True, help_text='财运')
    family = CharField(max_length=500, null=True, help_text='家宅')
    health = CharField(max_length=500, null=True, help_text='身体')
    gy_sort = IntegerField(null=True, help_text='卦序或爻序')
    
    class Meta:
        table_name = 'zy_gy'  # 指定表名
        
    @classmethod
    def get_by_id(cls, id):
        """
        根据id查询单条数据
        :param id: 记录ID
        :return: 返回查询到的记录，如果不存在则返回None
        """
        try:
            return cls.get(cls.id == id)
        except DoesNotExist:
            return None
        
    def __str__(self):
        return f"ZyGy(name={self.gy_name}, sort={self.gy_sort})" 