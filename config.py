import os

class Config:
    """应用配置"""
    AUDIO_FOLDER = os.getenv(
        "AUDIO_FOLDER", 
        "/mnt/shareEEx/liuyang/code/emotion_labeling_refactoring/data/emotion_annotation"
    )
    LABEL_FOLDER = os.getenv(
        "LABEL_FOLDER", 
        "/mnt/shareEEx/liuyang/code/emotion_labeling_refactoring/labels"
    )
    TEST_AUDIO_FOLDER = os.getenv(
        "TEST_AUDIO_FOLDER",
        "/mnt/shareEEx/liuyang/code/emotion_labeling_refactoring/data/test_examples"
    )
    ORDER_LIST_FOLDER = "order_list"
    
    # Flask配置
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 5000
    
    # 确保必要目录存在
    @classmethod
    def init_directories(cls):
        os.makedirs(cls.LABEL_FOLDER, exist_ok=True)
        os.makedirs(cls.ORDER_LIST_FOLDER, exist_ok=True)