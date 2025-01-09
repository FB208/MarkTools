from peewee import *
from .base_model import BaseModel

class WechatUser(BaseModel):
    """微信用户表"""
    id = AutoField(primary_key=True)
    nickname = CharField(max_length=100, null=True, help_text='昵称')
    base_info = CharField(max_length=500, null=True, help_text='基础信息')
    personality_summary = TextField(null=True, help_text='个性摘要')

    class Meta:
        table_name = 'wechat_user'

    @classmethod
    def create_user(cls, nickname=None, base_info=None, personality_summary=None):
        """创建用户"""
        return cls.create(
            nickname=nickname,
            base_info=base_info,
            personality_summary=personality_summary
        )

    @classmethod
    def get_by_id(cls, user_id):
        """根据ID获取用户"""
        return cls.get_or_none(cls.id == user_id)

    @classmethod
    def get_by_nickname(cls, nickname):
        """根据昵称查询用户
        
        Args:
            nickname: 用户昵称
            
        Returns:
            返回查询到的用户列表，如果没有找到返回空列表
        """
        return list(cls.select().where(cls.nickname == nickname))

    @classmethod
    def create_or_update_by_nickname(cls, nickname, **kwargs):
        """根据昵称创建或更新用户
        
        Args:
            nickname: 用户昵称
            **kwargs: 其他需要更新的字段，如 base_info, personality_summary
                     如果这些字段为None，则不会覆盖已有的值
            
        Returns:
            tuple: (user, created)
            - user: 创建或更新后的用户对象
            - created: 布尔值，True表示新创建，False表示更新
        """
        users = cls.get_by_nickname(nickname)
        if users:
            # 更新已存在的用户（取第一个）
            user = users[0]
            # 只更新非空值
            if kwargs.get('base_info') is not None:
                user.base_info = kwargs['base_info']
            if kwargs.get('personality_summary') is not None:
                user.personality_summary = kwargs['personality_summary']
            user.save()
            return user, False
        else:
            # 创建新用户
            kwargs['nickname'] = nickname
            return cls.create_user(**kwargs), True

    def update_info(self, **kwargs):
        """更新用户信息"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()

    def delete_user(self):
        """删除用户"""
        return self.delete_instance()

    def __str__(self):
        return f"WechatUser(id={self.id}, nickname={self.nickname})" 