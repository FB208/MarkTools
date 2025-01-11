from peewee import *
from datetime import datetime
from .base_model import BaseModel

class StarbotFriend(BaseModel):
    """星球好友表"""
    id = AutoField(primary_key=True)
    wx_id = CharField(max_length=100, unique=True, null=False, help_text='微信唯一标识')
    base_info = CharField(max_length=500, null=True, help_text='基础信息')
    personality_summary = TextField(null=True, help_text='个性摘要')
    created_at = DateTimeField(null=True, default=datetime.now)
    updated_at = DateTimeField(null=True, default=datetime.now)

    class Meta:
        table_name = 'starbot_friend'

    @classmethod
    def create_friend(cls, wx_id, base_info=None, personality_summary=None):
        """创建好友记录"""
        now = datetime.now()
        return cls.create(
            wx_id=wx_id,
            base_info=base_info,
            personality_summary=personality_summary,
            created_at=now,
            updated_at=now
        )

    @classmethod
    def get_by_id(cls, friend_id):
        """根据ID获取好友"""
        return cls.get_or_none(cls.id == friend_id)

    @classmethod
    def get_by_wx_id(cls, wx_id):
        """根据微信ID获取好友"""
        return cls.get_or_none(cls.wx_id == wx_id)

    @classmethod
    def create_or_update_by_wx_id(cls, wx_id, **kwargs):
        """根据微信ID创建或更新好友
        
        Args:
            wx_id: 微信唯一标识
            **kwargs: 其他需要更新的字段，如 base_info, personality_summary
                     如果这些字段为None，则不会覆盖已有的值
            
        Returns:
            tuple: (friend, created)
            - friend: 创建或更新后的好友对象
            - created: 布尔值，True表示新创建，False表示更新
        """
        friend = cls.get_by_wx_id(wx_id)
        if friend:
            # 更新已存在的好友
            update_data = {'updated_at': datetime.now()}
            if kwargs.get('base_info') is not None:
                update_data['base_info'] = kwargs['base_info']
            if kwargs.get('personality_summary') is not None:
                update_data['personality_summary'] = kwargs['personality_summary']
            friend.update_info(**update_data)
            return friend, False
        else:
            # 创建新好友
            kwargs['wx_id'] = wx_id
            return cls.create_friend(**kwargs), True

    def update_info(self, **kwargs):
        """更新好友信息"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
        self.save()

    def delete_friend(self):
        """删除好友"""
        return self.delete_instance()

    def __str__(self):
        return f"StarbotFriend(id={self.id}, wx_id={self.wx_id})" 
    
