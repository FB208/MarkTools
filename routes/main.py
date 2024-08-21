from flask import current_app as app
from flask import render_template
from . import main_bp

@main_bp.route('/')
def index():
    return render_template('home.html')

@main_bp.route('/login')
def login():
    return render_template('login.html')

@main_bp.route('/home')
def home():
    return render_template('home.html')