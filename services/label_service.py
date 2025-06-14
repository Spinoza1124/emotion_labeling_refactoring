import os
import re
from models.emotion_model import EmotionLabel, calculate_annotation_completeness
from utils.file_utils import safe_json_load, safe_json_save
from utils.audio_utils import get_audio_duration
from config import Config

class LabelService:
    """标注相关服务"""
    
    @staticmethod
    def get_labeled_files(username, speaker):
        """获取已标注的文件列表"""
        if not username:
            return set(), {}
            
        user_label_dir = os.path.join(Config.LABEL_FOLDER, username)
        labeled_files = set()
        annotation_completeness = {}
        
        if not os.path.exists(user_label_dir):
            return labeled_files, annotation_completeness
        
        # 处理分组说话人
        if re.match(r'spk\d+$', speaker):
            all_speakers = [
                d for d in os.listdir(Config.AUDIO_FOLDER)
                if os.path.isdir(os.path.join(Config.AUDIO_FOLDER, d)) 
                and d.startswith(speaker + '-')
            ]
            for sub_speaker in all_speakers:
                labeled, completeness = LabelService._get_speaker_labels(
                    user_label_dir, sub_speaker
                )
                labeled_files.update(labeled)
                annotation_completeness.update(completeness)
        else:
            labeled_files, annotation_completeness = LabelService._get_speaker_labels(
                user_label_dir, speaker
            )
        
        return labeled_files, annotation_completeness
    
    @staticmethod
    def _get_speaker_labels(user_label_dir, speaker):
        """获取单个说话人的标注数据"""
        label_path = os.path.join(user_label_dir, f"{speaker}_labels.json")
        labels = safe_json_load(label_path, [])
        
        labeled_files = set()
        annotation_completeness = {}
        
        for item in labels:
            audio_file = item["audio_file"]
            labeled_files.add(audio_file)
            annotation_completeness[audio_file] = calculate_annotation_completeness(item)
        
        return labeled_files, annotation_completeness
    
    @staticmethod
    def save_label(label_data, speaker, audio_file_path):
        """保存标注数据"""
        # 获取音频时长
        audio_duration = get_audio_duration(audio_file_path)
        
        # 创建标注对象
        label = EmotionLabel(
            audio_file=label_data.get("audio_file"),
            v_value=label_data.get("v_value"),
            a_value=label_data.get("a_value"),
            emotion_type=label_data.get("emotion_type"),
            discrete_emotion=label_data.get("discrete_emotion"),
            username=label_data.get("username"),
            patient_status=label_data.get("patient_status"),
            audio_duration=audio_duration
        )
        
        # 保存到文件
        user_label_dir = os.path.join(Config.LABEL_FOLDER, label.username)
        os.makedirs(user_label_dir, exist_ok=True)
        
        label_path = os.path.join(user_label_dir, f"{speaker}_labels.json")
        labels = safe_json_load(label_path, [])
        
        # 检查是否已存在
        existing_index = next(
            (i for i, item in enumerate(labels) 
             if item["audio_file"] == label.audio_file), None
        )
        
        if existing_index is not None:
            labels[existing_index] = label.to_dict()
        else:
            labels.append(label.to_dict())
        
        safe_json_save(label_path, labels)
        return True
    
    @staticmethod
    def get_label(username, speaker, filename):
        """获取特定音频的标注数据"""
        user_label_dir = os.path.join(Config.LABEL_FOLDER, username)
        
        if not os.path.exists(user_label_dir):
            return None
    
    @staticmethod
    def save_play_count(username, speaker, filename):
        """保存音频播放次数"""
        user_label_dir = os.path.join(Config.LABEL_FOLDER, username)
        
        if not os.path.exists(user_label_dir):
            return 0
        
        # 处理分组说话人
        if re.match(r'spk\d+$', speaker):
            all_speakers = [
                d for d in os.listdir(Config.AUDIO_FOLDER)
                if os.path.isdir(os.path.join(Config.AUDIO_FOLDER, d)) 
                and d.startswith(speaker + '-')
            ]
            
            for sub_speaker in all_speakers:
                count = LabelService._save_speaker_play_count(user_label_dir, sub_speaker, filename)
                if count > 0:
                    return count
        else:
            return LabelService._save_speaker_play_count(user_label_dir, speaker, filename)
        
        return 0
    
    @staticmethod
    def _save_speaker_play_count(user_label_dir, speaker, filename):
        """保存单个说话人的音频播放次数"""
        label_path = os.path.join(user_label_dir, f"{speaker}_labels.json")
        labels = safe_json_load(label_path, [])
        
        for label in labels:
            if label.get("audio_file") == filename:
                # 增加播放次数
                current_count = label.get("play_count", 0)
                label["play_count"] = current_count + 1
                
                # 保存更新后的数据
                safe_json_save(label_path, labels)
                return label["play_count"]
        
        return 0
    
    @staticmethod
    def get_play_count(username, speaker, filename):
        """获取音频播放次数"""
        user_label_dir = os.path.join(Config.LABEL_FOLDER, username)
        
        if not os.path.exists(user_label_dir):
            return 0
        
        # 处理分组说话人
        if re.match(r'spk\d+$', speaker):
            all_speakers = [
                d for d in os.listdir(Config.AUDIO_FOLDER)
                if os.path.isdir(os.path.join(Config.AUDIO_FOLDER, d)) 
                and d.startswith(speaker + '-')
            ]
            
            for sub_speaker in all_speakers:
                count = LabelService._get_speaker_play_count(user_label_dir, sub_speaker, filename)
                if count > 0:
                    return count
        else:
            return LabelService._get_speaker_play_count(user_label_dir, speaker, filename)
        
        return 0
    
    @staticmethod
    def _get_speaker_play_count(user_label_dir, speaker, filename):
        """获取单个说话人的音频播放次数"""
        label_path = os.path.join(user_label_dir, f"{speaker}_labels.json")
        labels = safe_json_load(label_path, [])
        
        for label in labels:
            if label.get("audio_file") == filename:
                return label.get("play_count", 0)
        
        return 0
        
        # 处理分组说话人
        if re.match(r'spk\d+$', speaker):
            all_speakers = [
                d for d in os.listdir(Config.AUDIO_FOLDER)
                if os.path.isdir(os.path.join(Config.AUDIO_FOLDER, d)) 
                and d.startswith(speaker + '-')
            ]
            
            for sub_speaker in all_speakers:
                label = LabelService._get_speaker_label(user_label_dir, sub_speaker, filename)
                if label:
                    return label
        else:
            return LabelService._get_speaker_label(user_label_dir, speaker, filename)
        
        return None
    
    @staticmethod
    def _get_speaker_label(user_label_dir, speaker, filename):
        """获取单个说话人的特定音频标注"""
        label_path = os.path.join(user_label_dir, f"{speaker}_labels.json")
        labels = safe_json_load(label_path, [])
        
        for label in labels:
            if label.get("audio_file") == filename:
                completeness = calculate_annotation_completeness(label)
                label["annotation_completeness"] = completeness
                return label
        
        return None