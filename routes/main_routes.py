from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route("/login")
def login():
    return render_template("login.html")

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route('/test')
def test_page():
    """测试页面"""
    return render_template('test.html')

@main_bp.route("/clear_login", methods=["GET"])
def clear_login():
    """清除登录状态，用于测试"""
    html = """
    <html>
    <head>
        <title>清除登录状态</title>
        <script>
            localStorage.removeItem('emotion_labeling_username');
            setTimeout(function() {
                window.location.href = '/';
            }, 1000);
        </script>
    </head>
    <body>
        <p>登录状态已清除，正在跳转...</p>
    </body>
    </html>
    """
    return html