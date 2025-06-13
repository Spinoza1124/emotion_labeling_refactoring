from pydub import AudioSegment
import pydub.exceptions

def get_audio_duration(file_path):
    """获取音频文件的时长（秒）"""
    try:
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000.0  # 毫秒转换为秒
    except pydub.exceptions.CouldntDecodeError:
        print(f"无法解码音频文件: {file_path}")
        return 0.0
    except Exception as e:
        print(f"获取音频时长时出错: {e}")
        return 0.0