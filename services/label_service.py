import os
from services.database_service import DatabaseService

class LabelService:
    """标注相关服务"""
    
    @staticmethod
    def get_labeled_files(username, speaker):
        """获取已标注的文件列表"""
        return DatabaseService.get_labeled_files(username, speaker)
    

    
    @staticmethod
    def save_label(label_data, speaker, audio_file_path):
        """保存标注数据到数据库"""
        return DatabaseService.save_label(label_data, speaker, audio_file_path)
    

    
    @staticmethod
    def get_label(username, speaker, filename):
        """获取标注数据"""
        return DatabaseService.get_label(username, speaker, filename)
    

    
    @staticmethod
    def save_play_count(username, speaker, filename):
        """保存音频播放次数"""
        return DatabaseService.update_play_count(username, speaker, filename)
    

    
    @staticmethod
    def get_play_count(username, speaker, filename):
        """获取音频播放次数"""
        return DatabaseService.get_play_count(username, speaker, filename)