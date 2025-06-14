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

def migrate_json_to_db():
    """
    将现有的JSON文件数据迁移到数据库
    """
    from utils.file_utils import safe_json_load
    
    db_path = os.path.join(Config.DATABASE_FOLDER, 'emotion_labels.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    migrated_count = 0
    
    # 遍历所有用户目录
    for username in os.listdir(Config.DATABASE_FOLDER):
        user_dir = os.path.join(Config.DATABASE_FOLDER, username)
        
        if not os.path.isdir(user_dir):
            continue
            
        # 遍历用户的标注文件
        for filename in os.listdir(user_dir):
            if not filename.endswith('_labels.json'):
                continue
                
            speaker = filename.replace('_labels.json', '')
            file_path = os.path.join(user_dir, filename)
            
            # 读取JSON数据
            labels = safe_json_load(file_path, [])
            
            for label in labels:
                try:
                    # 插入到数据库
                    cursor.execute('''
                        INSERT OR REPLACE INTO emotion_labels (
                            audio_file, speaker, username, v_value, a_value,
                            emotion_type, discrete_emotion, patient_status,
                            audio_duration, play_count, va_complete, discrete_complete,
                            timestamp
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        label.get('audio_file'),
                        speaker,
                        label.get('username'),
                        label.get('v_value'),
                        label.get('a_value'),
                        label.get('emotion_type'),
                        label.get('discrete_emotion'),
                        label.get('patient_status'),
                        label.get('audio_duration', 0),
                        label.get('play_count', 0),
                        label.get('va_complete', False),
                        label.get('discrete_complete', False),
                        label.get('timestamp')
                    ))
                    migrated_count += 1
                except Exception as e:
                    print(f"迁移数据时出错: {e}")
                    print(f"问题数据: {label}")
    
    conn.commit()
    conn.close()
    
    print(f"成功迁移 {migrated_count} 条标注数据到数据库")

if __name__ == '__main__':
    init_database()
    migrate_json_to_db()