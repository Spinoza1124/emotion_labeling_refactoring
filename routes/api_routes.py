import os
import re
from flask import Blueprint, jsonify, request, session, send_from_directory
from services.audio_service import AudioService
from services.label_service import LabelService
from services.user_service import UserService
from models.user_model import UserModel
from utils.logger import emotion_logger, log_api_call, get_client_ip
import traceback

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route("/speakers")
@log_api_call
def get_speakers():
    """获取所有说话人列表（查询参数方式）"""
    try:
        username = request.args.get('username', 'default')
        speakers = AudioService.get_speakers_list(username)
        
        emotion_logger.log_user_activity(
            username=username,
            action="获取说话人列表",
            details={"speaker_count": len(speakers)},
            ip_address=get_client_ip()
        )
        
        return jsonify(speakers)
    except Exception as e:
        emotion_logger.log_error(e, "获取说话人列表失败", username)
        return jsonify({"error": str(e)}), 500

@api_bp.route("/speakers/<username>")
def get_speakers_by_path(username):
    """获取所有说话人列表（路径参数方式）"""
    try:
        speakers = AudioService.get_speakers_list(username)
        return jsonify(speakers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route("/audio_list/<speaker>")
@log_api_call
def get_audio_list(speaker):
    """获取指定说话人的音频文件列表（查询参数方式）"""
    try:
        username = request.args.get('username', '')
        audio_files = AudioService.get_audio_files_list(speaker, username)
        labeled_files, annotation_completeness = LabelService.get_labeled_files(username, speaker)
        
        result = []
        for audio_file in audio_files:
            file_name = os.path.basename(audio_file)
            result.append({
                "file_name": file_name,
                "path": f"/api/audio/{speaker}/{file_name}",
                "labeled": file_name in labeled_files,
                "annotation_completeness": annotation_completeness.get(file_name, ['none']),
            })
        
        emotion_logger.log_user_activity(
            username=username,
            action="获取音频列表",
            details={"speaker": speaker, "audio_count": len(result)},
            ip_address=get_client_ip()
        )
        
        return jsonify(result)
    except Exception as e:
        emotion_logger.log_error(e, f"获取音频列表失败 - speaker: {speaker}", username)
        return jsonify({"error": str(e)}), 500

@api_bp.route("/audio_list/<username>/<speaker>")
def get_audio_list_by_path(username, speaker):
    """获取指定说话人的音频文件列表（路径参数方式）"""
    try:
        audio_files = AudioService.get_audio_files_list(speaker, username)
        labeled_files, annotation_completeness = LabelService.get_labeled_files(username, speaker)
        
        result = []
        for audio_file in audio_files:
            file_name = os.path.basename(audio_file)
            result.append({
                "file_name": file_name,
                "path": f"/api/audio/{speaker}/{file_name}",
                "labeled": file_name in labeled_files,
                "annotation_completeness": annotation_completeness.get(file_name, ['none']),
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route("/audio/<speaker>/<filename>")
@log_api_call
def get_audio(speaker, filename):
    """提供音频文件下载"""
    try:
        username = session.get('username', 'anonymous')
        file_path, actual_speaker = AudioService.find_audio_file(speaker, filename)
        if file_path:
            directory = os.path.dirname(file_path)
            
            emotion_logger.log_user_activity(
                username=username,
                action="获取音频文件",
                details={"speaker": speaker, "audio_file": filename},
                ip_address=get_client_ip()
            )
            
            return send_from_directory(directory, filename)
        else:
            emotion_logger.log_error(f"找不到音频文件 {filename}", "获取音频文件", username)
            return jsonify({"error": f"找不到音频文件 {filename}"}), 404
    except Exception as e:
        emotion_logger.log_error(e, f"获取音频文件失败 - speaker: {speaker}, file: {filename}", session.get('username'))
        return jsonify({"error": str(e)}), 500

@api_bp.route("/save_label", methods=["POST"])
@log_api_call
def save_label():
    """保存情感标注结果"""
    try:
        data = request.json
        speaker = data.get("speaker")
        audio_file = data.get("audio_file")
        username = data.get("username")
        
        if not all([speaker, audio_file, username]):
            emotion_logger.log_error("缺少必要参数", "保存标注", username)
            return jsonify({"error": "缺少必要参数"}), 400
        
        # 查找音频文件
        file_path, actual_speaker = AudioService.find_audio_file(speaker, audio_file)
        if not file_path:
            emotion_logger.log_error(f"找不到音频文件 {audio_file}", "保存标注", username)
            return jsonify({"error": f"找不到音频文件 {audio_file}"}), 404
        
        # 保存标注
        success = LabelService.save_label(data, actual_speaker, file_path)
        if success:
            # 记录标注活动
            emotion_logger.log_annotation_activity(
                username=username,
                speaker=speaker,
                audio_file=audio_file,
                action="保存",
                annotation_data=data
            )
            return jsonify({"success": True})
        else:
            emotion_logger.log_error("保存失败", "保存标注", username)
            return jsonify({"error": "保存失败"}), 500
            
    except Exception as e:
        emotion_logger.log_error(e, "保存标注失败", username, traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@api_bp.route("/get_label/<username>/<speaker>/<filename>")
@log_api_call
def get_label(username, speaker, filename):
    """获取特定音频的标注数据"""
    try:
        label = LabelService.get_label(username, speaker, filename)
        if label:
            emotion_logger.log_annotation_activity(
                username=username,
                speaker=speaker,
                audio_file=filename,
                action="加载",
                annotation_data=label
            )
            return jsonify({"success": True, "data": label})
        else:
            emotion_logger.log_error("未找到该音频的标注数据", "获取标注", username)
            return jsonify({"error": "未找到该音频的标注数据"}), 404
    except Exception as e:
        emotion_logger.log_error(e, f"获取标注失败 - speaker: {speaker}, file: {filename}", username)
        return jsonify({"error": str(e)}), 500

@api_bp.route("/update_username", methods=["POST"])
@log_api_call
def update_username():
    """更新用户名"""
    try:
        data = request.json
        old_username = data.get("old_username")
        new_username = data.get("new_username")
        current_user = session.get('username', 'anonymous')
        
        if not old_username or not new_username:
            emotion_logger.log_error("缺少必要参数", "更新用户名", current_user)
            return jsonify({"error": "缺少必要参数"}), 400
        
        moved_count = UserService.update_username(old_username, new_username)
        
        emotion_logger.log_user_activity(
            username=current_user,
            action="更新用户名",
            details={"old_username": old_username, "new_username": new_username},
            ip_address=get_client_ip()
        )
        
        return jsonify({"success": True, "moved_files": moved_count})
        
    except Exception as e:
        emotion_logger.log_error(e, f"更新用户名失败 - {old_username} -> {new_username}", current_user)
        return jsonify({"error": str(e)}), 500

# 添加播放计数相关的API端点
@api_bp.route("/save_play_count", methods=["POST"])
@log_api_call
def save_play_count():
    """保存音频播放计数"""
    try:
        data = request.json
        username = data.get("username")
        speaker = data.get("speaker") 
        audio_file = data.get("audio_file")
        
        if not all([username, speaker, audio_file]):
            emotion_logger.log_error("缺少必要参数", "保存播放次数", username)
            return jsonify({"error": "缺少必要参数"}), 400
        
        # 使用标签服务保存播放次数
        play_count = LabelService.save_play_count(username, speaker, audio_file)
        
        emotion_logger.log_user_activity(
            username=username,
            action="更新播放次数",
            details={
                "speaker": speaker,
                "audio_file": audio_file,
                "play_count": play_count
            },
            ip_address=get_client_ip()
        )
        
        return jsonify({
            "success": True,
            "play_count": play_count
        })
        
    except Exception as e:
        emotion_logger.log_error(e, "保存播放次数失败", username)
        return jsonify({"error": str(e)}), 500

@api_bp.route("/get_play_count/<username>/<speaker>/<filename>")
def get_play_count(username, speaker, filename):
    """获取音频播放计数"""
    try:
        # 使用标签服务获取播放次数
        play_count = LabelService.get_play_count(username, speaker, filename)
        
        return jsonify({
            "success": True,
            "play_count": play_count
        })
        
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/user/test-settings', methods=['POST'])
def get_user_test_settings():
    """获取用户的测试设置"""
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'success': False, 'message': '用户名不能为空'}), 400
        
        # 获取用户测试设置
        settings = UserModel().get_user_test_settings(username)
        
        return jsonify({
            'success': True,
            'skip_test': settings.get('skip_test', False),
            'skip_consistency_test': settings.get('skip_consistency_test', False)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户设置失败: {str(e)}'}), 500

@api_bp.route('/user/test-settings/<username>', methods=['GET'])
def get_user_test_settings_by_username(username):
    """通过用户名获取用户的测试设置"""
    try:
        if not username:
            return jsonify({'success': False, 'message': '用户名不能为空'}), 400
        
        # 获取用户测试设置
        settings = UserModel().get_user_test_settings(username)
        
        if settings is None:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        return jsonify({
            'success': True,
            'skip_test': settings.get('skip_test', False),
            'skip_consistency_test': settings.get('skip_consistency_test', False)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户设置失败: {str(e)}'}), 500

@api_bp.route('/user/session-status', methods=['GET'])
def get_session_status():
    """检查用户会话状态"""
    try:
        # 检查用户是否已登录
        if 'username' in session and session.get('authenticated', False):
            return jsonify({
                'authenticated': True,
                'username': session['username']
            })
        else:
            return jsonify({
                'authenticated': False
            })
            
    except Exception as e:
        return jsonify({
            'authenticated': False,
            'error': str(e)
        }), 500