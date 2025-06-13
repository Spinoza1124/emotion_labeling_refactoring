from flask import Flask
from config import Config
from routes.main_routes import main_bp
from routes.api_routes import api_bp
from routes.test_routes import test_bp

def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 配置session
    app.secret_key = 'emotion_labeling_secret_key_2024'  # 生产环境中应使用环境变量
    app.config['SESSION_TYPE'] = 'filesystem'
    
    # 初始化配置
    Config.init_directories()
    
    # 注册蓝图
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(test_bp)
    
    return app

# 为了兼容现有的启动脚本
app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)