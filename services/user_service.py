import os
import shutil
from config import Config
from utils.file_utils import safe_json_load, safe_json_save
from services.order_service import OrderService
from services.database_service import DatabaseService

class UserService:
    """用户相关服务"""
    
    @staticmethod
    def update_username(old_username, new_username):
        """更新用户名并移动文件"""
        old_user_dir = os.path.join(Config.DATABASE_FOLDER, old_username)
        new_user_dir = os.path.join(Config.DATABASE_FOLDER, new_username)
        
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
        
        # 更新数据库中的用户排序数据
        UserService._update_user_orders_in_db(old_username, new_username)
        
        return moved_count
    
    @staticmethod
    def _update_user_orders_in_db(old_username, new_username):
        """
        更新数据库中的用户排序数据
        
        Args:
            old_username (str): 旧用户名
            new_username (str): 新用户名
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 更新说话人排序表中的用户名
            cursor.execute(
                "UPDATE user_speaker_orders SET username = ? WHERE username = ?",
                (new_username, old_username)
            )
            
            # 更新音频排序表中的用户名
            cursor.execute(
                "UPDATE user_audio_orders SET username = ? WHERE username = ?",
                (new_username, old_username)
            )
            
            # 更新情感标注表中的用户名
            cursor.execute(
                "UPDATE emotion_labels SET username = ? WHERE username = ?",
                (new_username, old_username)
            )
            
            conn.commit()
            conn.close()
            
            print(f"已更新数据库中用户 {old_username} 的数据为 {new_username}")
            
        except Exception as e:
            print(f"更新数据库中用户数据失败: {e}")
    
    @staticmethod
    def delete_user_data(username):
        """
        删除用户的所有数据
        
        Args:
            username (str): 用户名
        """
        try:
            # 删除数据库中的排序数据
            OrderService.delete_user_orders(username)
            
            # 删除数据库中的标注数据
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM emotion_labels WHERE username = ?",
                (username,)
            )
            
            conn.commit()
            conn.close()
            
            # 删除文件系统中的用户目录（如果存在）
            user_dir = os.path.join(Config.DATABASE_FOLDER, username)
            if os.path.exists(user_dir):
                shutil.rmtree(user_dir)
            
            print(f"已删除用户 {username} 的所有数据")
            
        except Exception as e:
            print(f"删除用户数据失败: {e}")