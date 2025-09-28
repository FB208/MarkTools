from peewee import *
from .base_model import BaseModel

class CreditCard(BaseModel):
    """信用卡表"""
    id = AutoField(primary_key=True)  # 修改为 AutoField 对应自增主键
    v2user_id = BigIntegerField(null=True, help_text='V2 用户ID')
    card_code = CharField(max_length=50, null=True, help_text='卡号')
    credit_year = IntegerField(null=True, help_text='年份')
    credit_month = IntegerField(null=True, help_text='月份')
    bank = CharField(max_length=255, null=True, help_text='银行')
    repayment_date = CharField(max_length=255, null=True, help_text='还款日')
    annual_fee = DecimalField(max_digits=10, decimal_places=2, null=True, help_text='年费')
    free_need_count = IntegerField(null=True, help_text='免年费刷卡次数')
    
    class Meta:
        table_name = 'credit_card'  # 指定表名
        
    def __str__(self):
        return f"CreditCard(bank={self.bank}, card_code=****{self.card_code[-4:] if self.card_code else ''})"
        
    @property
    def masked_card_code(self):
        """获取掩码后的卡号"""
        if not self.card_code:
            return None
        return f"****{self.card_code[-4:]}"