import os
import sys
from flask import Flask

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    with app.app_context():
        from routes import main_bp, translate_bp, md2all_bp
        app.register_blueprint(main_bp)
        app.register_blueprint(translate_bp)
        app.register_blueprint(md2all_bp)
        
        return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)