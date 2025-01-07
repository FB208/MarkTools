from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from utils.mysql_util import db
from . import auth_bp



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
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.get_or_none(User.username == username):
            flash('用户名已存在')
            return render_template('auth/register.html')
            
        if User.get_or_none(User.email == email):
            flash('邮箱已被注册')
            return render_template('auth/register.html')
            
        with db.atomic():
            user = User(username=username, email=email)
            user.set_password(password)
            user.save()
            
        flash('注册成功，请登录')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index')) 