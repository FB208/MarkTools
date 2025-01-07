from peewee import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .base_model import BaseModel
from datetime import datetime

class User(UserMixin, BaseModel):
    """用户表"""
    id = AutoField(primary_key=True)
    username = CharField(max_length=80, unique=True, null=False)
    email = CharField(max_length=120, unique=True, null=False)
    password_hash = CharField(max_length=128)
    is_active = BooleanField(default=True)
    register_date = DateTimeField(default=datetime.now)  # 注册日期
    last_login_date = DateTimeField(null=True)  # 最后登录日期
    
    class Meta:
        table_name = 'users'
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login_date = datetime.now()
        self.save()
        
    def __str__(self):
        return f"User(username={self.username}, email={self.email})" 