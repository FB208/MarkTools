from peewee import *
from datetime import datetime
from utils.mysql_util import db

class BaseModel(Model):
    """基础模型类，所有模型都应该继承这个类"""
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        """重写save方法，自动更新updated_at字段"""
        self.updated_at = datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        database = db
        legacy_table_names = False  # 所有表名使用小写