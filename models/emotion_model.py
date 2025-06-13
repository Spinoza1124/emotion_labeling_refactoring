# models/emotion_model.py
from datetime import datetime

class EmotionLabel:
    """情感标注数据模型"""
    
    def __init__(self, audio_file, v_value, a_value, emotion_type="non-neutral", 
                 discrete_emotion=None, username=None, patient_status="patient", 
                 audio_duration=0):
        self.audio_file = audio_file
        self.v_value = v_value
        self.a_value = a_value
        self.emotion_type = emotion_type
        self.discrete_emotion = discrete_emotion
        self.username = username
        self.patient_status = patient_status
        self.audio_duration = audio_duration
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "audio_file": self.audio_file,
            "v_value": self.v_value,
            "a_value": self.a_value,
            "emotion_type": self.emotion_type,
            "discrete_emotion": self.discrete_emotion,
            "username": self.username,
            "patient_status": self.patient_status,
            "audio_duration": self.audio_duration,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        label = cls(
            data.get("audio_file"),
            data.get("v_value"),
            data.get("a_value"),
            data.get("emotion_type", "non-neutral"),
            data.get("discrete_emotion"),
            data.get("username"),
            data.get("patient_status", "patient"),
            data.get("audio_duration", 0)
        )
        if "timestamp" in data:
            label.timestamp = data["timestamp"]
        return label

def calculate_annotation_completeness(label_dict):
    """计算标注的完整性状态"""
    v_value = label_dict.get('v_value', 0)
    a_value = label_dict.get('a_value', 0)
    patient_status = label_dict.get('patient_status')
    emotion_type = label_dict.get('emotion_type')
    discrete_emotion = label_dict.get('discrete_emotion')
    
    has_va = v_value != 0 or a_value != 0
    has_patient_status = patient_status is not None
    has_emotion_type = emotion_type is not None
    
    # 检查离散情感是否完整标注
    has_discrete_emotion = False
    if emotion_type == 'neutral':
        # 对于中性情感，不需要额外的离散情感标注
        has_discrete_emotion = True
    elif emotion_type == 'non-neutral' and discrete_emotion is not None:
        # 对于非中性情感，需要有具体的离散情感标注
        has_discrete_emotion = True
    
    # 如果什么都没有标注
    if not has_va and not has_patient_status and not has_emotion_type:
        return 'none'
    
    # 如果所有必要的标注都完成了
    if has_va and has_patient_status and has_emotion_type and has_discrete_emotion:
        return 'complete'
    
    # 如果只标注了VA值或部分标注
    if has_va:
        return 'va-only'
    
    # 其他情况（只有patient_status或emotion_type但没有VA值）
    return 'none'