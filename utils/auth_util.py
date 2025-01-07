from functools import wraps
from flask import redirect, url_for
from flask_login import current_user

def login_required_ajax(func):
    """用于AJAX请求的登录验证装饰器"""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return {'error': '请先登录'}, 401
        return func(*args, **kwargs)
    return decorated_view 