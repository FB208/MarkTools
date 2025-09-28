from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask import current_app as app
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from utils.mysql_util import db
from . import auth_bp
import re
import requests



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False) == 'on'
        
        user = User.get_or_none(User.username == username)
        
        if user is not None and user.check_password(password):
            login_user(user, remember=remember)
            user.update_last_login()
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            return redirect(next_page)
        flash('用户名或密码错误')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # GET 正常渲染页面
    if request.method == 'GET':
        return render_template('auth/register.html')

    # POST：直接转调统一身份服务，保留主要逻辑
    payload = request.get_json(silent=True) or {}
    mtv2_base_url = app.config['MTV2_BASE_URL']
    mtv2_api_token = app.config['MTV2_API_TOKEN']
    upstream_url = f"{mtv2_base_url}auth/register"

    body = {
        "email": payload.get('email'),
        "code": payload.get('code'),
        "nikename": payload.get('nikename') or payload.get('username'),
        "password": payload.get('password') or '',
        "platform": app.config.get('PLATFORM', 'marktools'),
        "platform_version": app.config.get('PLATFORM_VERSION', '1.0.0'),
    }

    try:
        resp = requests.post(upstream_url, headers={"Authorization": f"Bearer {mtv2_api_token}"}, json=body, timeout=12)
        data = resp.json()
    except Exception:
        return jsonify({"success": False, "message": "注册失败，请稍后重试"}), 502

    if data.get('success') and isinstance(data.get('data'), dict):
        access_token = data['data'].get('access_token')
        token_type = data['data'].get('token_type')
        user_info = data['data'].get('user')
        if access_token and token_type:
            session['access_token'] = access_token
            session['token_type'] = token_type
            session['ext_user'] = user_info
            # 构造会话用户并登录
            try:
                from models.session_user import SessionUser
                su = SessionUser.from_dict(user_info)
                if su and su.get_id() is not None:
                    login_user(su, remember=True)
            except Exception:
                pass

    return jsonify(data), resp.status_code

@auth_bp.route('/send_code', methods=['GET', 'POST'])
def send_code():
    # 仅支持 POST JSON
    if request.method != 'POST':
        return jsonify({"success": False, "message": "Method Not Allowed"}), 405

    try:
        payload = request.get_json(silent=True) or {}
        email = (payload.get('email') or '').strip()
    except Exception:
        return jsonify({"success": False, "message": "请求体解析失败"}), 400

    if not email:
        return jsonify({"success": False, "message": "邮箱不能为空"}), 400

    # 简单的邮箱格式校验
    if not re.match(r"^.+@.+\..+$", email):
        return jsonify({"success": False, "message": "邮箱格式不正确"}), 400
    mtv2_base_url = app.config['MTV2_BASE_URL']
    mtv2_api_token = app.config['MTV2_API_TOKEN']
    upstream_url = f'{mtv2_base_url}email/send_verify_code'
    try:
        resp = requests.post(
            upstream_url,
            headers={
                "Authorization": f"Bearer {mtv2_api_token}"
            },
            json={
                "email": email,
                "display_name": "MarkTools"
            },
            timeout=10
        )
    except requests.RequestException:
        return jsonify({"success": False, "message": "发送失败，请稍后重试"}), 502

    # 尝试解析上游返回
    try:
        data = resp.json()
    except ValueError:
        return jsonify({"success": False, "message": "上游服务返回异常"}), 502

    success = bool(data.get('success'))
    message = data.get('message') or ('发送成功' if success else '发送失败')
    expire_minutes = None
    if isinstance(data.get('data'), dict):
        expire_minutes = data['data'].get('expire_minutes')

    result = {
        "success": success,
        "message": message,
    }
    if expire_minutes is not None:
        result["expire_minutes"] = expire_minutes

    status_code = 200 if success else 500
    return jsonify(result), status_code

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index')) 