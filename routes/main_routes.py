from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, make_response
from functools import wraps
from datetime import timedelta
from models.user_model import UserModel

main_bp = Blueprint('main', __name__)
user_model = UserModel()

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    """登录页面和登录处理"""
    if request.method == "GET":
        return render_template("login.html")
    
    # 处理POST请求 - 登录验证
    data = request.get_json() if request.is_json else request.form
    wechat_name = data.get('text1', '').strip()
    phone_number = data.get('password', '').strip()
    
    if not wechat_name or not phone_number:
        if request.is_json:
            return jsonify({'success': False, 'message': '请填写完整的微信昵称和手机号'}), 400
        return render_template("login.html", error="请填写完整的微信昵称和手机号")
    
    # 验证用户信息
    if user_model.verify_user(wechat_name, phone_number):
        # 设置安全的会话
        session.permanent = True  # 设置为永久会话
        session['username'] = wechat_name
        session['authenticated'] = True
        
        # 检查用户测试跳过设置
        test_settings = user_model.get_user_test_settings(wechat_name)
        
        if request.is_json:
            response_data = {
                'success': True, 
                'message': '登录成功', 
                'username': wechat_name,
                'skip_test': test_settings.get('skip_test', False),
                'skip_consistency_test': test_settings.get('skip_consistency_test', False)
            }
            response = make_response(jsonify(response_data))
            # 确保Cookie安全设置
            response.set_cookie('session_active', 'true', httponly=True, secure=False, samesite='Lax')
            return response
        
        # 根据测试设置决定重定向页面
        if not test_settings.get('skip_test', False):
            return redirect(url_for('main.test_page'))
        elif not test_settings.get('skip_consistency_test', False):
            return redirect('/consistency_test')
        else:
            return redirect(url_for('main.main_page'))
    else:
        # 用户不存在，自动注册
        if user_model.add_user(wechat_name, phone_number):
            # 设置安全的会话
            session.permanent = True  # 设置为永久会话
            session['username'] = wechat_name
            session['authenticated'] = True
            
            # 注册成功后，同样检查测试跳过设置
            test_settings = user_model.get_user_test_settings(wechat_name)
            
            if request.is_json:
                response_data = {
                    'success': True, 
                    'message': '注册并登录成功', 
                    'username': wechat_name,
                    'skip_test': test_settings.get('skip_test', False),
                    'skip_consistency_test': test_settings.get('skip_consistency_test', False)
                }
                response = make_response(jsonify(response_data))
                # 确保Cookie安全设置
                response.set_cookie('session_active', 'true', httponly=True, secure=False, samesite='Lax')
                return response
            
            # 根据测试设置决定重定向页面
            if not test_settings.get('skip_test', False):
                return redirect(url_for('main.test_page'))
            elif not test_settings.get('skip_consistency_test', False):
                return redirect('/consistency_test') # 注意：这里可能需要调整为 url_for('main.consistency_test_page') 或类似路由
            else:
                return redirect(url_for('main.main_page'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'message': '登录失败，请重试'}), 400
            return render_template("login.html", error="登录失败，请重试")

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查会话是否存在且已认证
        if 'username' not in session or not session.get('authenticated', False):
            # 清除可能存在的无效会话
            session.clear()
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route("/")
def index():
    """主页 - 重定向到登录页面"""
    return redirect(url_for('main.login'))

@main_bp.route("/main")
@login_required
def main_page():
    """主页面"""
    return render_template("index.html")

@main_bp.route('/test')
@login_required
def test_page():
    """测试页面"""
    return render_template('test.html')

@main_bp.route("/logout", methods=["GET", "POST"])
def logout():
    """退出登录"""
    # 完全清除会话
    session.clear()
    
    # 创建响应并清除相关Cookie
    response = make_response(redirect(url_for('main.login')))
    response.set_cookie('session_active', '', expires=0, httponly=True, secure=False, samesite='Lax')
    
    return response