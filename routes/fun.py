from flask import render_template, request, jsonify
from . import fun_bp
from services.credit_card_service import get_credit_cards, add_swipe_record
from flask_login import login_required

@fun_bp.route('/cyber_king')
def cyber_king():
    """赛博阎王"""
  
    return render_template('fun/cyber_king.html')

