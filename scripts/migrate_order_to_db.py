#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁移order_list文件夹到数据库
将用户的排序信息从JSON文件迁移到数据库表中
"""

import os
import sys
import sqlite3
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from utils.file_utils import safe_json_load

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

def migrate_order_data():
    """
    迁移order_list文件夹中的数据到数据库
    """
    order_list_folder = "order_list"  # 硬编码路径，因为这是迁移脚本
    
    if not os.path.exists(order_list_folder):
        print(f"order_list文件夹不存在: {order_list_folder}")
        return
    
    db_path = os.path.join(Config.DATABASE_FOLDER, 'emotion_labels.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 遍历用户文件夹
    for username in os.listdir(order_list_folder):
        user_folder = os.path.join(order_list_folder, username)
        if not os.path.isdir(user_folder):
            continue
            
        print(f"迁移用户 {username} 的排序数据...")
        
        # 迁移说话人排序
        speaker_order_file = os.path.join(user_folder, "speakers_order.json")
        if os.path.exists(speaker_order_file):
            speaker_order = safe_json_load(speaker_order_file, [])
            if speaker_order:
                cursor.execute('''
                    INSERT OR REPLACE INTO user_speaker_orders 
                    (username, speaker_order, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    username,
                    json.dumps(speaker_order, ensure_ascii=False),
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                print(f"  - 迁移说话人排序: {len(speaker_order)} 个说话人")
        
        # 迁移音频文件排序
        for filename in os.listdir(user_folder):
            if filename.endswith("_audio_order.json"):
                speaker = filename.replace("_audio_order.json", "")
                audio_order_file = os.path.join(user_folder, filename)
                audio_order = safe_json_load(audio_order_file, [])
                
                if audio_order:
                    cursor.execute('''
                        INSERT OR REPLACE INTO user_audio_orders 
                        (username, speaker, audio_order, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        username,
                        speaker,
                        json.dumps(audio_order, ensure_ascii=False),
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
                    print(f"  - 迁移音频排序 {speaker}: {len(audio_order)} 个文件")
    
    conn.commit()
    conn.close()
    print("数据迁移完成")

def verify_migration():
    """
    验证迁移结果
    """
    db_path = os.path.join(Config.DATABASE_FOLDER, 'emotion_labels.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查说话人排序表
    cursor.execute("SELECT COUNT(*) FROM user_speaker_orders")
    speaker_count = cursor.fetchone()[0]
    print(f"用户说话人排序记录数: {speaker_count}")
    
    # 检查音频排序表
    cursor.execute("SELECT COUNT(*) FROM user_audio_orders")
    audio_count = cursor.fetchone()[0]
    print(f"用户音频排序记录数: {audio_count}")
    
    # 显示一些示例数据
    cursor.execute("SELECT username, speaker_order FROM user_speaker_orders LIMIT 3")
    for row in cursor.fetchall():
        username, speaker_order = row
        order_list = json.loads(speaker_order)
        print(f"用户 {username} 的说话人排序: {order_list[:5]}...")
    
    cursor.execute("SELECT username, speaker, audio_order FROM user_audio_orders LIMIT 3")
    for row in cursor.fetchall():
        username, speaker, audio_order = row
        order_list = json.loads(audio_order)
        print(f"用户 {username} 的 {speaker} 音频排序: {order_list[:3]}...")
    
    conn.close()

def main():
    """
    主函数
    """
    print("开始迁移order_list到数据库...")
    
    # 创建数据库表
    create_order_tables()
    
    # 迁移数据
    migrate_order_data()
    
    # 验证迁移结果
    verify_migration()
    
    print("\n迁移完成！")
    print("注意: 迁移完成后，可以删除order_list文件夹")

if __name__ == "__main__":
    main()