from peewee import AutoField, CharField, Model

from utils.mysql_util import db


class AIModel(Model):
    """AI 模型配置表"""

    id = AutoField(primary_key=True)
    platform = CharField(max_length=50, null=True, help_text='平台')
    ai_type = CharField(max_length=50, null=True, help_text='用途')
    ai_model = CharField(max_length=50, null=True, help_text='所使用的模型')

    class Meta:
        table_name = 'ai_model'
        database = db

    def to_dict(self):
        return {
            'id': self.id,
            'platform': self.platform,
            'ai_type': self.ai_type,
            'ai_model': self.ai_model,
        }

