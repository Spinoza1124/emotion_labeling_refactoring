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

@admin_bp.route('/api/consistency/stats')
def get_consistency_stats():
    """
    获取一致性测试统计信息
    
    Returns:
        JSON响应，包含一致性测试统计信息
    """
    try:
        from services.database_service import DatabaseService
        
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        # 获取参与一致性测试的用户数
        cursor.execute('SELECT COUNT(DISTINCT username) FROM consistency_test_results')
        users_count = cursor.fetchone()[0] or 0
        
        # 获取总测试样本数
        cursor.execute('SELECT COUNT(*) FROM consistency_test_results')
        samples_count = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'users_count': users_count,
            'samples_count': samples_count
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/users/test-settings', methods=['GET'])
@admin_required
def get_users_test_settings():
    """
    获取所有用户的测试跳过设置
    
    Returns:
        JSON响应，包含所有用户的测试设置信息
    """
    try:
        from models.user_model import UserModel
        
        user_model = UserModel()
        users = user_model.get_all_users()
        
        return jsonify({
            'success': True,
            'users': users
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/users/test-settings', methods=['POST'])
@admin_required
def update_user_test_settings():
    """
    更新用户的测试跳过设置
    
    Returns:
        JSON响应，包含更新结果
    """
    try:
        from models.user_model import UserModel
        
        data = request.get_json()
        username = data.get('username')
        skip_test = data.get('skip_test')
        skip_consistency_test = data.get('skip_consistency_test')
        
        if not username:
            return jsonify({"error": "用户名不能为空"}), 400
        
        user_model = UserModel()
        success = user_model.update_user_test_settings(
            username, 
            skip_test=skip_test, 
            skip_consistency_test=skip_consistency_test
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '用户测试设置更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户不存在或更新失败'
            }), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/consistency/users')
def get_consistency_users():
    """
    获取参与一致性测试的用户列表
    
    Returns:
        JSON响应，包含用户列表
    """
    try:
        from services.database_service import DatabaseService
        
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT username FROM consistency_test_results ORDER BY username')
        users = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'users': users
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/consistency/calculate/<username>')
def calculate_user_consistency(username):
    """
    计算指定用户的一致性
    
    Args:
        username (str): 用户名
        
    Returns:
        JSON响应，包含用户一致性分析结果
    """
    try:
        import json
        import os
        from services.database_service import DatabaseService
        
        # 获取用户的一致性测试结果
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT audio_file, v_value, a_value, emotion_type, discrete_emotion, patient_status
            FROM consistency_test_results 
            WHERE username = ?
        ''', (username,))
        
        user_results = cursor.fetchall()
        conn.close()
        
        if not user_results:
            return jsonify({
                'success': False,
                'error': '该用户没有一致性测试数据'
            }), 404
        
        # 读取标准答案
        consistency_dir = '/mnt/shareEEx/liuyang/code/emotion_labeling_refactoring/data/consistency_test'
        standard_answers = {}
        
        for filename in os.listdir(consistency_dir):
            if filename.endswith('.json'):
                json_path = os.path.join(consistency_dir, filename)
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    audio_file = data.get('audio_file')
                    if audio_file:
                        standard_answers[audio_file] = data
        
        # 计算一致性
        total_samples = len(user_results)
        consistency_scores = {
            'v_value': 0,
            'a_value': 0,
            'emotion_type': 0,
            'discrete_emotion': 0,
            'patient_status': 0
        }
        
        detailed_results = []
        
        for result in user_results:
            audio_file = result[0]
            user_v = result[1]
            user_a = result[2]
            user_emotion_type = result[3]
            user_discrete = result[4]
            user_patient = result[5]
            
            if audio_file in standard_answers:
                standard = standard_answers[audio_file]
                
                # V值一致性（允许±0.5误差）
                v_consistent = abs(float(user_v or 0) - float(standard.get('v_value', 0))) <= 0.5
                if v_consistent:
                    consistency_scores['v_value'] += 1
                
                # A值一致性（允许±0.5误差）
                a_consistent = abs(float(user_a or 0) - float(standard.get('a_value', 0))) <= 0.5
                if a_consistent:
                    consistency_scores['a_value'] += 1
                
                # 情感类型一致性
                emotion_type_consistent = user_emotion_type == standard.get('emotion_type')
                if emotion_type_consistent:
                    consistency_scores['emotion_type'] += 1
                
                # 离散情感一致性
                discrete_consistent = user_discrete == standard.get('discrete_emotion')
                if discrete_consistent:
                    consistency_scores['discrete_emotion'] += 1
                
                # 患者状态一致性
                patient_consistent = user_patient == standard.get('patient_status')
                if patient_consistent:
                    consistency_scores['patient_status'] += 1
                
                detailed_results.append({
                    'audio_file': audio_file,
                    'v_consistent': v_consistent,
                    'a_consistent': a_consistent,
                    'emotion_type_consistent': emotion_type_consistent,
                    'discrete_consistent': discrete_consistent,
                    'patient_consistent': patient_consistent,
                    'user_values': {
                        'v_value': user_v,
                        'a_value': user_a,
                        'emotion_type': user_emotion_type,
                        'discrete_emotion': user_discrete,
                        'patient_status': user_patient
                    },
                    'standard_values': standard
                })
        
        # 计算百分比
        consistency_percentages = {}
        for key, score in consistency_scores.items():
            consistency_percentages[key] = (score / total_samples * 100) if total_samples > 0 else 0
        
        # 计算总体一致性
        overall_consistency = sum(consistency_percentages.values()) / len(consistency_percentages)
        
        return jsonify({
            'success': True,
            'username': username,
            'total_samples': total_samples,
            'consistency_scores': consistency_scores,
            'consistency_percentages': consistency_percentages,
            'overall_consistency': overall_consistency,
            'detailed_results': detailed_results
        })
        
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