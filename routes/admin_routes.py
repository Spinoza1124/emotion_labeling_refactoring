# -*- coding: utf-8 -*-
"""
管理员路由
提供管理员后台管理功能的API接口
"""

import os
from flask import Blueprint, jsonify, request, render_template, session
from services.admin_service import AdminService
from services.user_service import UserService
from config import Config

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# 管理员认证装饰器
def admin_required(f):
    """
    管理员权限验证装饰器
    
    Args:
        f: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return jsonify({"error": "需要管理员权限"}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/login', methods=['GET'])
def admin_login_page():
    """
    管理员登录页面
    
    Returns:
        渲染的HTML登录页面
    """
    return render_template('admin_login.html')

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """
    管理员登录API
    
    Returns:
        JSON响应，包含登录结果
    """
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # 简单的管理员验证（生产环境应使用更安全的方式）
        if username == 'admin' and password == 'admin123':
            session['is_admin'] = True
            session['admin_username'] = username
            return jsonify({"success": True, "message": "登录成功"})
        else:
            return jsonify({"success": False, "message": "用户名或密码错误"}), 401
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/logout', methods=['POST'])
@admin_required
def admin_logout():
    """
    管理员登出
    
    Returns:
        JSON响应，包含登出结果
    """
    session.pop('is_admin', None)
    session.pop('admin_username', None)
    return jsonify({"success": True, "message": "登出成功"})

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """
    管理员仪表板页面
    
    Returns:
        渲染的HTML页面
    """
    return render_template('admin_dashboard.html')

@admin_bp.route('/api/overview')
@admin_required
def get_overview():
    """
    获取系统概览数据
    
    Returns:
        JSON响应，包含系统概览统计信息
    """
    try:
        overview_data = AdminService.get_system_overview()
        return jsonify(overview_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/users')
@admin_required
def get_users():
    """
    获取所有用户列表及其标注统计
    
    Returns:
        JSON响应，包含用户列表和统计信息
    """
    try:
        users_data = AdminService.get_users_statistics()
        return jsonify(users_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/users/<username>/details')
@admin_required
def get_user_details(username):
    """
    获取指定用户的详细标注信息
    
    Args:
        username (str): 用户名
        
    Returns:
        JSON响应，包含用户详细标注信息
    """
    try:
        user_details = AdminService.get_user_details(username)
        return jsonify(user_details)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/speakers')
@admin_required
def get_speakers_statistics():
    """
    获取所有说话人的标注统计
    
    Returns:
        JSON响应，包含说话人标注统计信息
    """
    try:
        speakers_data = AdminService.get_speakers_statistics()
        return jsonify(speakers_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/progress')
@admin_required
def get_annotation_progress():
    """
    获取标注进度统计
    
    Returns:
        JSON响应，包含标注进度信息
    """
    try:
        progress_data = AdminService.get_annotation_progress()
        return jsonify(progress_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/quality')
@admin_required
def get_annotation_quality():
    """
    获取标注质量分析
    
    Returns:
        JSON响应，包含标注质量分析数据
    """
    try:
        quality_data = AdminService.get_annotation_quality()
        return jsonify(quality_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/export')
@admin_required
def export_data():
    """
    导出标注数据
    
    Returns:
        JSON响应，包含导出文件信息
    """
    try:
        export_format = request.args.get('format', 'csv')
        username = request.args.get('username')
        speaker = request.args.get('speaker')
        
        export_result = AdminService.export_annotation_data(
            format=export_format,
            username=username,
            speaker=speaker
        )
        return jsonify(export_result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/users/<username>/reset', methods=['POST'])
@admin_required
def reset_user_progress(username):
    """
    重置用户标注进度
    
    Args:
        username (str): 用户名
        
    Returns:
        JSON响应，包含重置结果
    """
    try:
        result = AdminService.reset_user_progress(username)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/backup', methods=['POST'])
@admin_required
def backup_database():
    """
    备份数据库
    
    Returns:
        JSON响应，包含备份结果
    """
    try:
        backup_result = AdminService.backup_database()
        return jsonify(backup_result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/system/status')
@admin_required
def get_system_status():
    """
    获取系统状态信息
    
    Returns:
        JSON响应，包含系统状态信息
    """
    try:
        status_data = AdminService.get_system_status()
        return jsonify(status_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500