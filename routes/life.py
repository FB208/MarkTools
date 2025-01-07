from flask import render_template, request, jsonify
from . import life_bp
from services.credit_card_service import get_credit_cards, add_swipe_record
from flask_login import login_required

@life_bp.route('/credit_card')
@login_required
def credit_card():
    """信用卡管理页面"""
  
    return render_template('life/credit_card.html')

@life_bp.route('/credit_card/list', methods=['GET'])
@login_required
def credit_card_list():
    """信用卡列表接口"""
    credit_cards = get_credit_cards()
    return jsonify(credit_cards)

@life_bp.route('/credit_card/swipe', methods=['POST'])
@login_required
def swipe_card():
    """信用卡刷卡接口"""
    try:
        data = request.get_json()
        record_id = data.get('record_id')
        
        if not record_id:
            return jsonify({
                'success': False,
                'message': '记录ID不能为空'
            })
            
        result = add_swipe_record(record_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        })

