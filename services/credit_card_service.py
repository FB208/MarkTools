from utils.vika_util import VikaClient
from datetime import datetime, timedelta

def get_credit_cards():
    """
    从维格表获取信用卡信息，并按开卡月份计算年度刷卡次数
    
    Returns:
        list: 信用卡记录列表，每条记录包含基本信息和刷卡统计
    """
    try:
        vika_client = VikaClient()
        
        # 获取信用卡基本信息
        cards_result = vika_client.get_records(
            datasheet_id="dstGf7rE8sHNARigHC",
            pageSize=100
        )
        
        # 获取刷卡记录
        swipe_result = vika_client.get_records(
            datasheet_id="dst437HAGbxuGVuZHR",
            pageSize=1000
        )
        
        if not (cards_result['success'] and swipe_result['success']):
            return []
            
        cards = cards_result['data']['records']
        swipes = swipe_result['data']['records']
        
        # 获取当前日期
        now = datetime.now()
        
        # 计算每张卡的刷卡次数
        card_swipe_counts = {}
        for card in cards:
            card_number = card['fields'].get('卡号')
            card_month = int(card['fields'].get('月份', 1))
            
            # 计算统计区间
            if card_month <= now.month:
                # 如果开卡月份小于等于当前月份，统计区间是今年的开卡月份到现在
                start_date = datetime(now.year, card_month, 1)
                end_date = now + timedelta(days=1)  # 包含今天
            else:
                # 如果开卡月份大于当前月份，统计区间是去年的开卡月份到现在
                start_date = datetime(now.year - 1, card_month, 1)
                end_date = now + timedelta(days=1)  # 包含今天
            
            # 统计在区间内的刷卡次数
            swipe_count = 0
            for swipe in swipes:
                if swipe['fields'].get('卡号') == card_number:
                    swipe_time = datetime.fromtimestamp(swipe['fields'].get('刷卡时间') / 1000)
                    if start_date <= swipe_time < end_date:
                        swipe_count += 1
            
            card_swipe_counts[card_number] = swipe_count
            
            # 打印调试信息
            print(f"卡号: {card_number}")
            print(f"统计区间: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")
            print(f"刷卡次数: {swipe_count}")
        
        # 整合信息
        for card in cards:
            card_number = card['fields'].get('卡号')
            card_month = int(card['fields'].get('月份', 1))
            # 添加刷卡次数
            card['fields']['已刷次数'] = card_swipe_counts.get(card_number, 0)
            # 计算剩余应刷次数
            card['fields']['剩余应刷次数'] = max(0, card['fields'].get('免年费次数', 0) - card['fields']['已刷次数'])
            # 添加统计区间信息（方便前端显示）
            if card_month <= now.month:
                card['fields']['统计年度'] = f"{now.year}.{card_month:02d}-至今"
            else:
                card['fields']['统计年度'] = f"{now.year-1}.{card_month:02d}-至今"
            # 只保留卡号后四位
            if card_number:
                card['fields']['卡号'] = card_number[-4:]
        
        return cards
        
    except Exception as e:
        print(f"获取信用卡信息失败: {str(e)}")
        return []

def add_swipe_record(record_id):
    """
    添加信用卡刷卡记录
    
    Args:
        record_id: 信用卡记录ID
        
    Returns:
        dict: 包含操作结果的字典
        {
            'success': bool,  # 操作是否成功
            'message': str    # 结果信息
        }
    """
    try:
        vika_client = VikaClient()
        
        # 使用recordId查询卡片信息
        cards_result = vika_client.get_records(
            datasheet_id="dstGf7rE8sHNARigHC",
            filterByFormula="record_id='"+record_id+"'"
            # filterByFormula=f"{{recordId}}='{record_id}'"
        )
        
        if not cards_result['success']:
            return {
                'success': False,
                'message': '获取卡片信息失败'
            }
            
        cards = cards_result['data']['records']
        if not cards:
            return {
                'success': False,
                'message': '未找到对应的信用卡记录'
            }
            
        card = cards[0]
        card_number = card['fields'].get('卡号')
        
        # 获取当前时间戳（毫秒）
        current_time = int(datetime.now().timestamp() * 1000)
        
        # 创建刷卡记录
        result = vika_client.insert_records(
            datasheet_id="dst437HAGbxuGVuZHR",
            records=[{
                "fields": {
                    "卡号": card_number,
                    "刷卡时间": current_time
                }
            }]
        )
        
        if result['success']:
            return {
                'success': True,
                'message': '刷卡记录添加成功'
            }
        else:
            return {
                'success': False,
                'message': '刷卡记录添加失败'
            }
            
    except Exception as e:
        print(f"添加刷卡记录失败: {str(e)}")
        return {
            'success': False,
            'message': f'添加刷卡记录失败: {str(e)}'
        }