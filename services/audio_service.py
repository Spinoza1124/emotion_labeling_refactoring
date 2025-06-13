# services/audio_service.py
import os
import glob
import re
import random
from config import Config
from utils.file_utils import safe_json_load, safe_json_save

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
        order_dir = os.path.join(Config.ORDER_LIST_FOLDER, username)
        os.makedirs(order_dir, exist_ok=True)
        speaker_order_file = os.path.join(order_dir, "speakers_order.json")
        
        saved_order = safe_json_load(speaker_order_file)
        
        if saved_order:
            # 按保存的顺序重新排列
            sorted_groups = []
            existing_groups = set(speaker_groups.keys())
            for group in saved_order:
                if group in existing_groups:
                    sorted_groups.append(group)
                    existing_groups.remove(group)
            sorted_groups.extend(list(existing_groups))
        else:
            # 创建新的个性化排序
            speaker_group_list = list(speaker_groups.keys())
            random.seed(hash(username) % (2**32))
            random.shuffle(speaker_group_list)
            sorted_groups = speaker_group_list
            random.seed()
            
            # 保存排序
            safe_json_save(speaker_order_file, sorted_groups)
        
        return sorted_groups
    
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
        user_order_dir = os.path.join(Config.ORDER_LIST_FOLDER, username)
        os.makedirs(user_order_dir, exist_ok=True)
        audio_order_file = os.path.join(user_order_dir, f"{speaker}_audio_order.json")
        
        audio_file_names = [os.path.basename(f) for f in audio_files]
        saved_order = safe_json_load(audio_order_file)
        
        if saved_order:
            # 按保存的顺序排列
            sorted_files = []
            saved_names = set(saved_order)
            current_names = set(audio_file_names)
            
            # 添加已保存顺序的文件
            for name in saved_order:
                if name in current_names:
                    for full_path in audio_files:
                        if os.path.basename(full_path) == name:
                            sorted_files.append(full_path)
                            break
            
            # 添加新文件
            new_files = current_names - saved_names
            if new_files:
                new_file_paths = [f for f in audio_files if os.path.basename(f) in new_files]
                seed_string = f"{username}_{speaker}_new"
                random.seed(hash(seed_string) % (2**32))
                random.shuffle(new_file_paths)
                random.seed()
                sorted_files.extend(new_file_paths)
                
                # 更新保存的顺序
                updated_order = [os.path.basename(f) for f in sorted_files]
                safe_json_save(audio_order_file, updated_order)
        else:
            # 创建新的排序
            seed_string = f"{username}_{speaker}"
            random.seed(hash(seed_string) % (2**32))
            random.shuffle(audio_files)
            random.seed()
            sorted_files = audio_files
            
            # 保存排序
            audio_order = [os.path.basename(f) for f in sorted_files]
            safe_json_save(audio_order_file, audio_order)
        
        return sorted_files
    
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