import os
import sqlite3
from config import Config

class UserModel:
    """用户数据模型类"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.db_path = os.path.join(Config.DATABASE_FOLDER, 'users.db')
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wechat_name TEXT NOT NULL UNIQUE,
                phone_number TEXT NOT NULL,
                skip_test BOOLEAN DEFAULT FALSE,
                skip_consistency_test BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, wechat_name, phone_number):
        """添加新用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO users (wechat_name, phone_number) VALUES (?, ?)',
                (wechat_name, phone_number)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # 用户已存在
            return False
        finally:
            conn.close()
    
    def get_user(self, wechat_name):
        """根据微信昵称获取用户信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM users WHERE wechat_name = ?',
            (wechat_name,)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'wechat_name': user[1],
                'phone_number': user[2],
                'created_at': user[3]
            }
        return None
    
    def verify_user(self, wechat_name, phone_number):
        """验证用户登录信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM users WHERE wechat_name = ? AND phone_number = ?',
            (wechat_name, phone_number)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        return user is not None
    
    def get_all_users(self):
        """获取所有用户列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT wechat_name, phone_number, skip_test, skip_consistency_test, created_at FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        conn.close()
        
        return [{
            'wechat_name': user[0],
            'phone_number': user[1],
            'skip_test': bool(user[2]),
            'skip_consistency_test': bool(user[3]),
            'created_at': user[4]
        } for user in users]
    
    def update_user_test_settings(self, wechat_name, skip_test=None, skip_consistency_test=None):
        """
        更新用户的测试跳过设置
        
        Args:
            wechat_name (str): 用户微信昵称
            skip_test (bool, optional): 是否跳过能力测试
            skip_consistency_test (bool, optional): 是否跳过一致性测试
            
        Returns:
            bool: 更新是否成功
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 构建更新语句
            update_fields = []
            params = []
            
            if skip_test is not None:
                update_fields.append('skip_test = ?')
                params.append(skip_test)
            
            if skip_consistency_test is not None:
                update_fields.append('skip_consistency_test = ?')
                params.append(skip_consistency_test)
            
            if not update_fields:
                return False
            
            params.append(wechat_name)
            
            cursor.execute(
                f'UPDATE users SET {", ".join(update_fields)} WHERE wechat_name = ?',
                params
            )
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"更新用户测试设置失败: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_test_settings(self, wechat_name):
        """
        获取用户的测试跳过设置
        
        Args:
            wechat_name (str): 用户微信昵称
            
        Returns:
            dict: 包含测试设置的字典，如果用户不存在返回None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT skip_test, skip_consistency_test FROM users WHERE wechat_name = ?',
            (wechat_name,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'skip_test': bool(result[0]),
                'skip_consistency_test': bool(result[1])
            }
        return None