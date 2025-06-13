import os
import shutil
from config import Config
from utils.file_utils import safe_json_load, safe_json_save

class UserService:
    """用户相关服务"""
    
    @staticmethod
    def update_username(old_username, new_username):
        """更新用户名并移动文件"""
        old_user_dir = os.path.join(Config.LABEL_FOLDER, old_username)
        new_user_dir = os.path.join(Config.LABEL_FOLDER, new_username)
        
        if not os.path.exists(old_user_dir):
            return 0
        
        os.makedirs(new_user_dir, exist_ok=True)
        moved_count = 0
        
        # 移动所有JSON文件并更新用户名
        for filename in os.listdir(old_user_dir):
            if filename.endswith('.json'):
                old_file_path = os.path.join(old_user_dir, filename)
                new_file_path = os.path.join(new_user_dir, filename)
                
                # 读取并更新用户名
                data = safe_json_load(old_file_path, [])
                for item in data:
                    if item.get("username") == old_username:
                        item["username"] = new_username
                
                # 保存到新位置
                safe_json_save(new_file_path, data)
                moved_count += 1
        
        # 删除旧目录
        if moved_count > 0:
            shutil.rmtree(old_user_dir)
        
        return moved_count