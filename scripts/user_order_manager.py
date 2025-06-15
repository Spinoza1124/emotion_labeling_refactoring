#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户排序数据管理模块
负责创建和管理用户的排序相关数据库表，并为新用户初始化默认排序
"""

import os
import sys
import sqlite3
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
# 移除了对file_utils的依赖，因为不再需要迁移order_list文件夹

def create_order_tables():
    """
    创建用户排序相关的数据库表
    """
    db_path = os.path.join(Config.DATABASE_FOLDER, 'emotion_labels.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建用户说话人排序表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_speaker_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            speaker_order TEXT NOT NULL,  -- JSON格式存储排序列表
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(username)
        )
    ''')
    
    # 创建用户音频文件排序表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_audio_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            speaker TEXT NOT NULL,
            audio_order TEXT NOT NULL,  -- JSON格式存储排序列表
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(username, speaker)
        )
    ''')
    
    # 创建索引
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_user_speaker_orders_username 
        ON user_speaker_orders(username)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_user_audio_orders_username_speaker 
        ON user_audio_orders(username, speaker)
    ''')
    
    # 创建触发器用于更新 updated_at
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_user_speaker_orders_timestamp 
        AFTER UPDATE ON user_speaker_orders
        BEGIN
            UPDATE user_speaker_orders SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = NEW.id;
        END
    ''')
    
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_user_audio_orders_timestamp 
        AFTER UPDATE ON user_audio_orders
        BEGIN
            UPDATE user_audio_orders SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = NEW.id;
        END
    ''')
    
    conn.commit()
    conn.close()
    print("数据库表创建成功")

def initialize_user_orders(username, speakers=None):
    """
    为新用户初始化排序数据
    
    Args:
        username (str): 用户名
        speakers (list, optional): 说话人列表，如果为None则使用默认列表
    
    Returns:
        bool: 初始化是否成功
    """
    # 首先确保数据库表存在
    create_order_tables()
    try:
        db_path = os.path.join(Config.DATABASE_FOLDER, 'emotion_labels.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查用户是否已存在排序记录
        cursor.execute("SELECT COUNT(*) FROM user_speaker_orders WHERE username = ?", (username,))
        if cursor.fetchone()[0] > 0:
            print(f"用户 {username} 的排序数据已存在，跳过初始化")
            conn.close()
            return True
        
        # 如果没有提供说话人列表，使用默认列表
        if speakers is None:
            speakers = ["spk182", "spk183", "spk184", "spk185", "spk186"]  # 默认说话人列表
        
        # 初始化说话人排序
        cursor.execute('''
            INSERT INTO user_speaker_orders 
            (username, speaker_order, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (
            username,
            json.dumps(speakers, ensure_ascii=False),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        # 为每个说话人初始化空的音频排序
        for speaker in speakers:
            cursor.execute('''
                INSERT INTO user_audio_orders 
                (username, speaker, audio_order, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                username,
                speaker,
                json.dumps([], ensure_ascii=False),  # 初始为空列表
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        print(f"成功为用户 {username} 初始化排序数据")
        return True
        
    except Exception as e:
        print(f"为用户 {username} 初始化排序数据时出错: {e}")
        return False






def ensure_user_orders_exist(username, speakers=None):
    """
    确保用户的排序数据存在，如果不存在则自动创建
    这个函数专门用于用户登录时调用，确保用户有完整的排序数据
    
    Args:
        username (str): 登录的用户名
        speakers (list, optional): 说话人列表，如果为None则使用默认列表
    
    Returns:
        bool: 操作是否成功
    """
    try:
        # 首先确保数据库表存在
        create_order_tables()
        
        db_path = os.path.join(Config.DATABASE_FOLDER, 'emotion_labels.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查用户是否已存在排序记录
        cursor.execute("SELECT COUNT(*) FROM user_speaker_orders WHERE username = ?", (username,))
        if cursor.fetchone()[0] > 0:
            # 用户排序数据已存在，无需创建
            conn.close()
            return True
        
        # 用户排序数据不存在，需要创建
        print(f"为新用户 {username} 创建排序数据...")
        
        # 如果没有提供说话人列表，使用默认列表
        if speakers is None:
            speakers = ["spk182", "spk183", "spk184", "spk185", "spk186"]  # 默认说话人列表
        
        # 初始化说话人排序
        cursor.execute('''
            INSERT INTO user_speaker_orders 
            (username, speaker_order, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (
            username,
            json.dumps(speakers, ensure_ascii=False),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        # 为每个说话人初始化空的音频排序
        for speaker in speakers:
            cursor.execute('''
                INSERT INTO user_audio_orders 
                (username, speaker, audio_order, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                username,
                speaker,
                json.dumps([], ensure_ascii=False),  # 初始为空列表
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        print(f"成功为用户 {username} 创建排序数据")
        return True
        
    except Exception as e:
        print(f"为用户 {username} 创建排序数据时出错: {e}")
        return False


def main():
    """
    主函数 - 用于测试新用户初始化
    """
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "init" and len(sys.argv) > 2:
            # 为指定用户初始化排序数据
            username = sys.argv[2]
            print(f"为用户 {username} 初始化排序数据...")
            
            # 初始化用户数据
            success = initialize_user_orders(username)
            if success:
                print(f"用户 {username} 排序数据初始化完成！")
            else:
                print(f"用户 {username} 排序数据初始化失败！")
            return
        elif sys.argv[1] == "ensure" and len(sys.argv) > 2:
            # 确保用户排序数据存在（用于登录时调用）
            username = sys.argv[2]
            print(f"确保用户 {username} 的排序数据存在...")
            
            success = ensure_user_orders_exist(username)
            if success:
                print(f"用户 {username} 排序数据检查完成！")
            else:
                print(f"用户 {username} 排序数据检查失败！")
            return
    
    # 默认行为：显示使用方法
    print("用户排序数据管理工具")
    print("\n使用方法:")
    print("  python migrate_order_to_db.py init <username>    # 为新用户初始化排序数据")
    print("  python migrate_order_to_db.py ensure <username>  # 确保用户排序数据存在（登录时使用）")

if __name__ == "__main__":
    main()