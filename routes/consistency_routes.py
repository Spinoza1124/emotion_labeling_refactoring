import os
import json
import glob
from flask import Blueprint, jsonify, request, send_from_directory, render_template
from config import Config
from services.database_service import DatabaseService

consistency_bp = Blueprint('consistency', __name__)

@consistency_bp.route('/consistency-test')
def consistency_test_page():
    """一致性测试页面"""
    return render_template('consistency_test.html')

@consistency_bp.route('/api/consistency/questions')
def get_consistency_questions():
    """获取一致性测试题目"""
    try:
        consistency_dir = '/mnt/shareEEx/liuyang/code/emotion_labeling_refactoring/data/consistency_test'
        
        if not os.path.exists(consistency_dir):
            return jsonify({
                'success': False,
                'error': '一致性测试数据目录不存在'
            }), 404
        
        questions = []
        
        # 获取所有音频文件
        audio_files = glob.glob(os.path.join(consistency_dir, '*.wav'))
        
        for audio_file in audio_files:
            filename = os.path.basename(audio_file)
            # 移除扩展名获取基础文件名
            base_name = os.path.splitext(filename)[0]
            
            questions.append({
                'filename': filename,
                'base_name': base_name,
                'type': 'consistency'
            })
        
        # 按文件名排序
        questions.sort(key=lambda x: x['filename'])
        
        return jsonify({
            'success': True,
            'questions': questions,
            'total_count': len(questions)
        })
        
    except Exception as e:
        print(f"获取一致性测试题目失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@consistency_bp.route('/api/consistency/audio/<filename>')
def get_consistency_audio(filename):
    """获取一致性测试音频文件"""
    try:
        consistency_dir = '/mnt/shareEEx/liuyang/code/emotion_labeling_refactoring/data/consistency_test'
        file_path = os.path.join(consistency_dir, filename)
        
        if os.path.exists(file_path):
            return send_from_directory(consistency_dir, filename)
        
        return jsonify({'error': '音频文件不存在'}), 404
        
    except Exception as e:
        print(f"获取一致性测试音频失败: {e}")
        return jsonify({'error': str(e)}), 500

@consistency_bp.route('/api/consistency/submit', methods=['POST'])
def submit_consistency_result():
    """提交一致性测试结果"""
    try:
        data = request.json
        username = data.get('username')
        results = data.get('results', [])
        
        if not username:
            return jsonify({'error': '缺少用户名'}), 400
        
        if not results:
            return jsonify({'error': '缺少测试结果'}), 400
        
        # 保存到数据库
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        # 创建一致性测试结果表（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consistency_test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                audio_file TEXT NOT NULL,
                v_value REAL,
                a_value REAL,
                emotion_type TEXT,
                discrete_emotion TEXT,
                patient_status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(username, audio_file)
            )
        ''')
        
        # 保存每个结果
        for result in results:
            cursor.execute('''
                INSERT OR REPLACE INTO consistency_test_results (
                    username, audio_file, v_value, a_value, emotion_type, 
                    discrete_emotion, patient_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                username,
                result.get('filename'),
                result.get('v_value'),
                result.get('a_value'),
                result.get('emotion_type'),
                result.get('discrete_emotion'),
                result.get('patient_status')
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'成功保存 {len(results)} 条一致性测试结果'
        })
        
    except Exception as e:
        print(f"提交一致性测试结果失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@consistency_bp.route('/api/consistency/history/<username>')
def get_consistency_history(username):
    """获取用户的一致性测试历史"""
    try:
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM consistency_test_results 
            WHERE username = ? 
            ORDER BY timestamp DESC
        ''', (username,))
        
        results = cursor.fetchall()
        conn.close()
        
        history = []
        for row in results:
            history.append({
                'id': row['id'],
                'audio_file': row['audio_file'],
                'v_value': row['v_value'],
                'a_value': row['a_value'],
                'emotion_type': row['emotion_type'],
                'discrete_emotion': row['discrete_emotion'],
                'patient_status': row['patient_status'],
                'timestamp': row['timestamp']
            })
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        print(f"获取一致性测试历史失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500