import os
from flask import Flask
from config import Config
from routes.main_routes import main_bp
from routes.api_routes import api_bp
from routes.test_routes import test_bp
from routes.consistency_routes import consistency_bp
from routes.admin_routes import admin_bp
from scripts.count_audio_files import update_audio_count_in_system

def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 配置安全的session
    app.secret_key = os.getenv('SECRET_KEY', 'emotion_labeling_secret_key_2024')  # 生产环境中应使用环境变量
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # 防止XSS攻击
    app.config['SESSION_COOKIE_SECURE'] = False  # 开发环境设为False，生产环境应设为True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # 防止CSRF攻击
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600 * 24  # 会话有效期24小时
    
    # 初始化配置
    Config.init_directories()
    
    # 注册蓝图
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(test_bp)  # 移除url_prefix，因为test_routes.py中已经包含了完整路径
    app.register_blueprint(consistency_bp)  # 注册一致性测试路由
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    return app

# 为了兼容现有的启动脚本
app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)