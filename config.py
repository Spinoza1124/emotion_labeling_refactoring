import os

class Config:
    """应用配置"""
    AUDIO_FOLDER = os.getenv(
        "AUDIO_FOLDER", 
        "/mnt/shareEEx/liuyang/code/emotion_labeling_refactoring/data/emotion_annotation"
    )
    DATABASE_FOLDER = os.getenv(
        "DATABASE_FOLDER", 
        "/mnt/shareEEx/liuyang/code/emotion_labeling_refactoring/database"
    )
    TEST_AUDIO_FOLDER = os.getenv(
        "TEST_AUDIO_FOLDER",
        "/mnt/shareEEx/liuyang/code/emotion_labeling_refactoring/data/test_examples"
    )
    
    # Flask配置
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 5000
    
    # 确保必要目录存在
    @classmethod
    def init_directories(cls):
        os.makedirs(cls.DATABASE_FOLDER, exist_ok=True)
        # os.makedirs(cls.ORDER_LIST_FOLDER, exist_ok=True)  # 已迁移到数据库