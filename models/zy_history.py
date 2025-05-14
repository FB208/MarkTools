from peewee import *
from .base_model import BaseModel

class ZyHistory(BaseModel):
    """占卜历史记录表"""
    id = AutoField(primary_key=True)
    chat_id = CharField(max_length=255, null=True, help_text='会话ID')
    user_id = IntegerField(null=True, help_text='用户ID')
    role = CharField(max_length=50, null=True, help_text='角色')
    content = TextField(null=True, help_text='内容')
    
    class Meta:
        table_name = 'zy_history'  # 指定表名
        
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
    
    @classmethod
    def get_by_chat_id(cls, chat_id):
        """
        根据chat_id查询会话历史记录
        :param chat_id: 会话ID
        :return: 返回查询到的记录列表
        """
        return cls.select().where(cls.chat_id == chat_id).order_by(cls.created_at)
    
    @classmethod
    def get_by_user_id(cls, user_id):
        """
        根据user_id查询用户的所有会话历史记录
        :param user_id: 用户ID
        :return: 返回查询到的记录列表
        """
        return cls.select().where(cls.user_id == user_id).order_by(cls.created_at.desc())
    
    @classmethod
    def insert_record(cls, chat_id, user_id, role, content):
        """
        插入一条历史记录，id自增
        :param chat_id: 会话ID
        :param user_id: 用户ID
        :param role: 角色
        :param content: 内容
        :return: 返回插入的记录
        """
        # 创建记录时不指定id，让数据库自动生成
        record = ZyHistory(
            chat_id=chat_id,
            user_id=user_id,
            role=role,
            content=content
        )
        # 保存记录
        record.save(force_insert=True)
        return record
    
    def __str__(self):
        return f"ZyHistory(id={self.id}, chat_id={self.chat_id}, role={self.role})" 