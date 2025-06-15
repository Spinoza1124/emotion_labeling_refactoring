#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一数据库初始化脚本
用于一次性创建所有必要的数据库表结构和初始化数据

功能包括：
1. 创建情感标注数据库表
2. 创建用户排序相关表
3. 创建分组分配相关表
4. 初始化用户数据库
5. 导入分组数据（如果存在）
"""

import sys
try:
    import sqlite3
except ImportError:
    print("SQLite3 模块不可用，请安装 sqlite3 或使用其他数据库")
    print("当前将使用 JSON 文件作为数据存储")
    sys.exit(0)

import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from models.user_model import UserModel


def init_emotion_labels_database():
    """
    初始化情感标注数据库，创建核心表结构
    """
    print("正在初始化情感标注数据库...")
    
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
    
    print(f"✓ 情感标注数据库初始化完成: {db_path}")


def init_user_order_tables():
    """
    创建用户排序相关的数据库表
    """
    print("正在创建用户排序相关表...")
    
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
    
    print("✓ 用户排序表创建完成")


def init_group_assignment_database():
    """
    创建分组分配数据库和相关表
    """
    print("正在创建分组分配数据库...")
    
    db_path = os.path.join(Config.DATABASE_FOLDER, 'group_assignments.db')
    
    # 确保目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建分组信息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS speaker_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            speaker_id TEXT NOT NULL,
            duration REAL NOT NULL,
            segment_count INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(group_id, speaker_id)
        )
    ''')
    
    # 创建分组分配表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'assigned',  -- assigned, in_progress, completed
            progress_count INTEGER DEFAULT 0,
            total_segments INTEGER DEFAULT 0,
            completed_at TIMESTAMP NULL,
            UNIQUE(group_id, username)
        )
    ''')
    
    # 创建分组状态表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_status (
            group_id INTEGER PRIMARY KEY,
            total_duration REAL NOT NULL,
            total_segments INTEGER NOT NULL,
            assigned_count INTEGER DEFAULT 0,
            completed_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'available',  -- available, in_progress, completed
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建用户标注进度表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_annotation_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            group_id INTEGER NOT NULL,
            speaker_id TEXT NOT NULL,
            audio_file TEXT NOT NULL,
            annotation_status TEXT DEFAULT 'pending',  -- pending, completed
            annotated_at TIMESTAMP NULL,
            va_value REAL NULL,
            a_value REAL NULL,
            emotion TEXT NULL,
            UNIQUE(username, group_id, audio_file)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✓ 分组分配数据库创建完成: {db_path}")
    return db_path


def import_group_data():
    """
    解析分组文件并导入数据到数据库
    """
    print("正在导入分组数据...")
    
    group_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', '分组.txt')
    
    if not os.path.exists(group_file_path):
        print(f"⚠ 分组文件不存在: {group_file_path}，跳过分组数据导入")
        return
    
    db_path = os.path.join(Config.DATABASE_FOLDER, 'group_assignments.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    current_group = 0
    group_total_duration = 0
    group_total_segments = 0
    
    with open(group_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            if line.startswith('=== 第'):
                # 如果之前有分组数据，先保存到group_status表
                if current_group > 0:
                    cursor.execute('''
                        INSERT OR REPLACE INTO group_status 
                        (group_id, total_duration, total_segments, status)
                        VALUES (?, ?, ?, 'available')
                    ''', (current_group, group_total_duration, group_total_segments))
                
                # 解析新分组
                group_num = line.split('第')[1].split('组')[0].strip()
                current_group = int(group_num)
                group_total_duration = 0
                group_total_segments = 0
                print(f"  处理第 {current_group} 组")
                
            elif ':' in line and '总时长' in line and '段数' in line:
                # 解析说话人数据
                parts = line.split(':')
                speaker_id = parts[0].strip()
                
                # 提取时长和段数
                info_part = parts[1].strip()
                duration_str = info_part.split('总时长')[1].split('秒')[0].strip()
                segments_str = info_part.split('段数')[1].strip()
                
                try:
                    duration = float(duration_str)
                    segments = int(segments_str)
                    
                    # 插入说话人数据
                    cursor.execute('''
                        INSERT OR REPLACE INTO speaker_groups 
                        (group_id, speaker_id, duration, segment_count)
                        VALUES (?, ?, ?, ?)
                    ''', (current_group, speaker_id, duration, segments))
                    
                    group_total_duration += duration
                    group_total_segments += segments
                    
                except ValueError as e:
                    print(f"  解析错误: {line}, 错误: {e}")
    
    # 保存最后一个分组的状态
    if current_group > 0:
        cursor.execute('''
            INSERT OR REPLACE INTO group_status 
            (group_id, total_duration, total_segments, status)
            VALUES (?, ?, ?, 'available')
        ''', (current_group, group_total_duration, group_total_segments))
    
    conn.commit()
    conn.close()
    
    print(f"✓ 分组数据导入完成，共处理 {current_group} 个分组")


def init_user_database():
    """
    初始化用户数据库
    """
    print("正在初始化用户数据库...")
    try:
        user_model = UserModel()
        print("✓ 用户数据库初始化完成")
    except Exception as e:
        print(f"⚠ 用户数据库初始化失败: {e}")


def main():
    """
    主函数：执行完整的数据库初始化流程
    """
    print("="*60)
    print("开始初始化情感标注系统数据库")
    print("="*60)
    
    try:
        # 1. 初始化情感标注数据库
        init_emotion_labels_database()
        
        # 2. 创建用户排序表
        init_user_order_tables()
        
        # 3. 创建分组分配数据库
        init_group_assignment_database()
        
        # 4. 导入分组数据
        import_group_data()
        
        # 5. 初始化用户数据库
        init_user_database()
        
        print("\n" + "="*60)
        print("✅ 数据库初始化完成！")
        print("="*60)
        print("\n已创建的数据库文件:")
        print(f"  - {os.path.join(Config.DATABASE_FOLDER, 'emotion_labels.db')}")
        print(f"  - {os.path.join(Config.DATABASE_FOLDER, 'group_assignments.db')}")
        print(f"  - {os.path.join(Config.DATABASE_FOLDER, 'users.db')}")
        print("\n现在可以启动应用程序了！")
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()