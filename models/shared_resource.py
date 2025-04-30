from peewee import *
from .base_model import BaseModel

class SharedResource(BaseModel):
    """共享资源模型类
    
    用于存储各种资源的链接和信息
    
    属性:
        id (str): 资源唯一标识符
        r_name (str): 资源名称
        r_value (str): 资源值/链接
    """
    id = CharField(primary_key=True, max_length=255)
    r_name = CharField(max_length=255, null=True)
    r_value = CharField(max_length=1000, null=True)
    
    class Meta:
        table_name = 'shared_resource'
    
    def to_dict(self):
        """将对象转换为字典
        
        返回:
            dict: 包含对象属性的字典
        """
        return {
            'id': self.id,
            'r_name': self.r_name,
            'r_value': self.r_value
        }
    
    def __repr__(self):
        return f"<SharedResource(id='{self.id}', r_name='{self.r_name}')>"
    
    @classmethod
    def get_by_id(cls, resource_id):
        """通过 id 查询单个共享资源
        
        参数:
            resource_id (str): 资源 id
            
        返回:
            SharedResource: 查询到的资源对象，如果不存在则返回 None
        """
        try:
            return cls.get(cls.id == resource_id)
        except cls.DoesNotExist:
            return None 