import os
import sys
import logging  # 添加logging导入

# 配置日志输出到标准输出，这样Docker可以捕获日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

from flask import Flask
from flask_cors import CORS
from flask_session import Session
from flask_login import LoginManager
from dotenv import load_dotenv
from cachelib import FileSystemCache

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 强制重新加载 .env 文件
load_dotenv(override=True)

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object('config.Config')
    app.config['SESSION_TYPE'] = 'filesystem'  # 使用文件系统来存储 session 数据
    app.config['SESSION_CACHE'] = FileSystemCache('./flask_session/', threshold=500, mode=0o600)
    app.config['SESSION_PERMANENT'] = True  # 设置为 True 使 session 持久化
    app.config['PERMANENT_SESSION_LIFETIME'] = 31 * 24 * 60 * 60  # 设置 session 有效期为31天
    app.config['SESSION_KEY_PREFIX'] = 'myapp_'  # session 数据前缀

    # 初始化 session
    Session(app)

    # 初始化 LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # 设置登录视图的端点
    login_manager.login_message = '请先登录'  # 设置登录提示消息

    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.get_or_none(User.id == int(user_id))

    with app.app_context():
        from routes import main_bp, translate_bp, md2all_bp, speech2text_bp, article_bp, test_bp, wechat_bp, starbot_bp, scheduler_bp, life_bp, word_plugin_bp, auth_bp, fun_bp, text2speech_bp, wechat_sub_account_bp, lighthouse_bp
        app.register_blueprint(main_bp)
        app.register_blueprint(translate_bp)
        app.register_blueprint(md2all_bp)
        app.register_blueprint(speech2text_bp)
        app.register_blueprint(article_bp)
        app.register_blueprint(test_bp)
        app.register_blueprint(wechat_bp)
        app.register_blueprint(starbot_bp)
        app.register_blueprint(scheduler_bp)
        app.register_blueprint(life_bp)
        app.register_blueprint(word_plugin_bp)
        app.register_blueprint(auth_bp)  # 注册认证蓝图
        app.register_blueprint(fun_bp)  # 注册娱乐蓝图
        app.register_blueprint(text2speech_bp)
        app.register_blueprint(wechat_sub_account_bp)
        app.register_blueprint(lighthouse_bp)  # 注册lighthouse蓝图
        return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)