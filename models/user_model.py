import sqlite3
import os
from config import Config

class UserModel:
    """用户数据模型类"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.db_path = os.path.join(Config.LABEL_FOLDER, 'users.db')
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
        
        cursor.execute('SELECT wechat_name, phone_number, created_at FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        conn.close()
        
        return [{
            'wechat_name': user[0],
            'phone_number': user[1],
            'created_at': user[2]
        } for user in users]