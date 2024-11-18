from peewee import *
from .base_model import BaseModel
from .credit_card import CreditCard

class CreditCardLog(BaseModel):
    """信用卡刷卡记录表"""
    id = AutoField(primary_key=True)  # 修改为 AutoField 对应自增主键
    card_code = CharField(max_length=50, null=True, help_text='卡号')
    insert_time = DateTimeField(null=True, help_text='刷卡时间')
    
    class Meta:
        table_name = 'credit_card_log'
        
    def __str__(self):
        return f"CreditCardLog(card_code=****{self.card_code[-4:] if self.card_code else ''}, insert_time={self.insert_time})"
    
    @property
    def credit_card(self):
        """获取关联的信用卡信息"""
        return CreditCard.get_or_none(CreditCard.card_code == self.card_code)