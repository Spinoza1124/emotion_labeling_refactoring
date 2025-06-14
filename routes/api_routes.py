import os
import re
from flask import Blueprint, jsonify, request, send_from_directory
from services.audio_service import AudioService
from services.label_service import LabelService
from services.user_service import UserService

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route("/speakers")
def get_speakers():
    """获取所有说话人列表（查询参数方式）"""
    try:
        username = request.args.get('username', 'default')
        speakers = AudioService.get_speakers_list(username)
        return jsonify(speakers)
    except Exception as e:
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
        
        return jsonify(result)
    except Exception as e:
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
def get_audio(speaker, filename):
    """提供音频文件下载"""
    try:
        file_path, actual_speaker = AudioService.find_audio_file(speaker, filename)
        if file_path:
            directory = os.path.dirname(file_path)
            return send_from_directory(directory, filename)
        else:
            return jsonify({"error": f"找不到音频文件 {filename}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route("/save_label", methods=["POST"])
def save_label():
    """保存情感标注结果"""
    try:
        data = request.json
        speaker = data.get("speaker")
        audio_file = data.get("audio_file")
        username = data.get("username")
        
        if not all([speaker, audio_file, username]):
            return jsonify({"error": "缺少必要参数"}), 400
        
        # 查找音频文件
        file_path, actual_speaker = AudioService.find_audio_file(speaker, audio_file)
        if not file_path:
            return jsonify({"error": f"找不到音频文件 {audio_file}"}), 404
        
        # 保存标注
        success = LabelService.save_label(data, actual_speaker, file_path)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "保存失败"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route("/get_label/<username>/<speaker>/<filename>")
def get_label(username, speaker, filename):
    """获取特定音频的标注数据"""
    try:
        label = LabelService.get_label(username, speaker, filename)
        if label:
            return jsonify({"success": True, "data": label})
        else:
            return jsonify({"error": "未找到该音频的标注数据"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route("/update_username", methods=["POST"])
def update_username():
    """更新用户名"""
    try:
        data = request.json
        old_username = data.get("old_username")
        new_username = data.get("new_username")
        
        if not old_username or not new_username:
            return jsonify({"error": "缺少必要参数"}), 400
        
        moved_count = UserService.update_username(old_username, new_username)
        return jsonify({"success": True, "moved_files": moved_count})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 添加播放计数相关的API端点
@api_bp.route("/save_play_count", methods=["POST"])
def save_play_count():
    """保存音频播放计数"""
    try:
        data = request.json
        username = data.get("username")
        speaker = data.get("speaker") 
        audio_file = data.get("audio_file")
        
        if not all([username, speaker, audio_file]):
            return jsonify({"error": "缺少必要参数"}), 400
        
        # 这里可以实现播放计数的保存逻辑
        # 暂时返回模拟数据
        play_count = 1  # 实际应该从数据库或文件中获取并递增
        
        return jsonify({
            "success": True,
            "play_count": play_count
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route("/get_play_count/<username>/<speaker>/<filename>")
def get_play_count(username, speaker, filename):
    """获取音频播放计数"""
    try:
        # 这里应该实现从数据库或文件中获取播放计数的逻辑
        # 暂时返回模拟数据
        play_count = 0
        
        return jsonify({
            "success": True,
            "play_count": play_count
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500