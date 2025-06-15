#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
用于创建情感标注数据库表结构
"""
import sys
try:
    import sqlite3
except ImportError:
    print("SQLite3 模块不可用，请安装 sqlite3 或使用其他数据库")
    print("当前将使用 JSON 文件作为数据存储")
    sys.exit(0)

import os
import sys
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from models.user_model import UserModel

def init_database():
    """
    初始化数据库，创建必要的表
    """
    db_path = os.path.join(Config.DATABASE_FOLDER, 'emotion_labels.db')
    
    # 确保目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建标注数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotion_labels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audio_file TEXT NOT NULL,
            speaker TEXT NOT NULL,
            username TEXT NOT NULL,
            v_value REAL,
            a_value REAL,
            emotion_type TEXT,
            discrete_emotion TEXT,
            patient_status TEXT,
            audio_duration REAL DEFAULT 0,
            play_count INTEGER DEFAULT 0,
            va_complete BOOLEAN DEFAULT FALSE,
            discrete_complete BOOLEAN DEFAULT FALSE,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(audio_file, speaker, username)
        )
    ''')
    
    # 创建索引以提高查询性能
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_audio_speaker_user 
        ON emotion_labels(audio_file, speaker, username)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_username_speaker 
        ON emotion_labels(username, speaker)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON emotion_labels(timestamp)
    ''')
    
    # 创建触发器，自动更新 updated_at 字段
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_emotion_labels_timestamp 
        AFTER UPDATE ON emotion_labels
        FOR EACH ROW
        BEGIN
            UPDATE emotion_labels SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = NEW.id;
        END
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"数据库初始化完成: {db_path}")
    
    # 初始化用户数据库
    print("正在初始化用户数据库...")
    user_model = UserModel()
    print("用户数据库初始化完成")


if __name__ == '__main__':
    init_database()
