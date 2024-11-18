import os
import sys
from flask import Flask
from flask_cors import CORS
from flask_session import Session
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
    app.config['SESSION_PERMANENT'] = False  # 如果为 False，则关闭浏览器后 session 失效
    app.config['SESSION_KEY_PREFIX'] = 'myapp_'  # session 数据前缀

    # 初始化 session
    Session(app)

    with app.app_context():
        from routes import main_bp, translate_bp, md2all_bp, speech2text_bp, article_bp, test_bp, wechat_bp, scheduler_bp, life_bp
        app.register_blueprint(main_bp)
        app.register_blueprint(translate_bp)
        app.register_blueprint(md2all_bp)
        app.register_blueprint(speech2text_bp)
        app.register_blueprint(article_bp)
        app.register_blueprint(test_bp)
        app.register_blueprint(wechat_bp)
        app.register_blueprint(scheduler_bp)
        app.register_blueprint(life_bp)
        return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)