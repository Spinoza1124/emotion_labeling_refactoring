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
    
    # 安全配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'emotion_labeling_secret_key_2024')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # 开发环境设为False，生产环境应设为True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600 * 24  # 24小时

    # 测试配置
    TEST_QUESTION_LIMIT = 1  # 测试题目数量限制
    
    # 确保必要目录存在
    @classmethod
    def init_directories(cls):
        os.makedirs(cls.DATABASE_FOLDER, exist_ok=True)
        # os.makedirs(cls.ORDER_LIST_FOLDER, exist_ok=True)  # 已迁移到数据库