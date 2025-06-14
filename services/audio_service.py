# services/audio_service.py
import os
import glob
import re
import random
from config import Config
from services.order_service import OrderService

class AudioService:
    """音频文件相关服务"""
    
    @staticmethod
    def get_speakers_list(username="default"):
        """获取说话人列表"""
        if not os.path.exists(Config.AUDIO_FOLDER):
            raise FileNotFoundError(f"音频文件夹不存在: {Config.AUDIO_FOLDER}")

        # 获取所有说话人目录
        all_speakers = [
            d for d in os.listdir(Config.AUDIO_FOLDER)
            if os.path.isdir(os.path.join(Config.AUDIO_FOLDER, d))
        ]
        
        # 按spk编号分组
        speaker_groups = {}
        for speaker in all_speakers:
            match = re.match(r'(spk)(\d+)-(\d+)-(\d+)', speaker)
            if match:
                prefix, spk_id, part, section = match.groups()
                spk_group = f"spk{spk_id}"
                if spk_group not in speaker_groups:
                    speaker_groups[spk_group] = []
                speaker_groups[spk_group].append(speaker)
            else:
                speaker_groups[speaker] = [speaker]
        
        # 获取或创建用户专属排序
        return AudioService._get_user_speaker_order(username, speaker_groups)
    
    @staticmethod
    def _get_user_speaker_order(username, speaker_groups):
        """获取用户专属的说话人排序"""
        return OrderService.get_user_speaker_order(username, speaker_groups)
    
    @staticmethod
    def get_audio_files_list(speaker, username=""):
        """获取指定说话人的音频文件列表"""
        # 获取音频文件
        if re.match(r'spk\d+$', speaker):
            audio_files = AudioService._get_grouped_speaker_files(speaker)
        else:
            audio_files = AudioService._get_single_speaker_files(speaker)
        
        # 获取用户专属的文件排序
        if username:
            audio_files = AudioService._get_user_audio_order(speaker, username, audio_files)
        else:
            random.shuffle(audio_files)
        
        return audio_files
    
    @staticmethod
    def _get_grouped_speaker_files(speaker):
        """获取分组说话人的音频文件"""
        all_speakers = [
            d for d in os.listdir(Config.AUDIO_FOLDER)
            if os.path.isdir(os.path.join(Config.AUDIO_FOLDER, d)) 
            and d.startswith(speaker + '-')
        ]
        
        audio_files = []
        for sub_speaker in all_speakers:
            speaker_folder = os.path.join(Config.AUDIO_FOLDER, sub_speaker)
            files = glob.glob(os.path.join(speaker_folder, "*.wav"))
            audio_files.extend(files)
        
        return audio_files
    
    @staticmethod
    def _get_single_speaker_files(speaker):
        """获取单个说话人的音频文件"""
        speaker_folder = os.path.join(Config.AUDIO_FOLDER, speaker)
        if not os.path.exists(speaker_folder):
            raise FileNotFoundError(f"找不到说话人 {speaker} 的文件夹")
        
        return glob.glob(os.path.join(speaker_folder, "*.wav"))
    
    @staticmethod
    def _get_user_audio_order(speaker, username, audio_files):
        """获取用户专属的音频文件排序"""
        return OrderService.get_user_audio_order(speaker, username, audio_files)
    
    @staticmethod
    def find_audio_file(speaker, filename):
        """查找音频文件的完整路径"""
        if re.match(r'spk\d+$', speaker):
            # 分组说话人
            all_speakers = [
                d for d in os.listdir(Config.AUDIO_FOLDER)
                if os.path.isdir(os.path.join(Config.AUDIO_FOLDER, d)) 
                and d.startswith(speaker + '-')
            ]
            
            for sub_speaker in all_speakers:
                file_path = os.path.join(Config.AUDIO_FOLDER, sub_speaker, filename)
                if os.path.exists(file_path):
                    return file_path, sub_speaker
            return None, None
        else:
            # 单个说话人
            file_path = os.path.join(Config.AUDIO_FOLDER, speaker, filename)
            if os.path.exists(file_path):
                return file_path, speaker
            return None, None