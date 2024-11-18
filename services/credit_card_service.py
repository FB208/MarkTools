from datetime import datetime, timedelta
from models import CreditCard, CreditCardLog
from utils.mysql_util import MySQLUtil

def get_credit_cards():
    """获取信用卡信息，并按开卡月份计算年度刷卡次数"""
    try:
        # 初始化数据库连接
        MySQLUtil.init_db()
        
        # 获取当前日期
        now = datetime.now()
        
        # 获取所有信用卡
        cards = CreditCard.select()
        result = []
        
        for card in cards:
            card_month = card.credit_month or 1
            
            # 计算统计区间
            if card_month <= now.month:
                start_date = datetime(now.year, card_month, 1)
            else:
                start_date = datetime(now.year - 1, card_month, 1)
            end_date = now + timedelta(days=1)  # 包含今天
            
            # 统计刷卡次数
            swipe_count = CreditCardLog.select().where(
                (CreditCardLog.card_code == card.card_code) &
                (CreditCardLog.insert_time >= start_date) &
                (CreditCardLog.insert_time < end_date)
            ).count()
            
            # 构造返回数据结构
            card_data = {
                'recordId': str(card.id),  # 保持与前端兼容
                'fields': {
                    'cardNumber': card.card_code[-4:] if card.card_code else '',
                    'bank': card.bank,
                    'month': card.credit_month,
                    'repaymentDate': card.repayment_date,
                    'annualFee': float(card.annual_fee) if card.annual_fee else 0,
                    'freeNeedCount': card.free_need_count or 0,
                    'swipeCount': swipe_count,
                    'remainingCount': max(0, (card.free_need_count or 0) - swipe_count),
                    'statYear': f"{now.year}.{card_month:02d}-至今" if card_month <= now.month else f"{now.year-1}.{card_month:02d}-至今"
                }
            }
            result.append(card_data)
            
        return result
        
    except Exception as e:
        print(f"获取信用卡信息失败: {str(e)}")
        return []
        
    finally:
        MySQLUtil.close_db()

def add_swipe_record(record_id):
    """添加信用卡刷卡记录"""
    try:
        MySQLUtil.init_db()
        
        # 查询信用卡信息
        card = CreditCard.get_or_none(CreditCard.id == record_id)
        if not card:
            return {
                'success': False,
                'message': '未找到对应的信用卡记录'
            }
        
        # 创建刷卡记录
        with MySQLUtil.transaction():
            CreditCardLog.create(
                card_code=card.card_code,
                insert_time=datetime.now()
            )
        
        return {
            'success': True,
            'message': '刷卡记录添加成功'
        }
            
    except Exception as e:
        print(f"添加刷卡记录失败: {str(e)}")
        return {
            'success': False,
            'message': f'添加刷卡记录失败: {str(e)}'
        }
        
    finally:
        MySQLUtil.close_db()