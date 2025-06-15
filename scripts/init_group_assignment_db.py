#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分组分配数据库初始化脚本
用于管理用户分组标注任务的分配和进度跟踪
"""

import sqlite3
import os
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def create_group_assignment_database():
    """
    创建分组分配数据库和相关表
    """
    db_path = os.path.join(Config.DATABASE_FOLDER, 'group_assignments.db')
    
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
    
    print(f"分组分配数据库已创建: {db_path}")
    return db_path

def parse_group_file_and_insert_data():
    """
    解析分组文件并插入数据到数据库
    """
    group_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', '分组.txt')
    
    if not os.path.exists(group_file_path):
        print(f"分组文件不存在: {group_file_path}")
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
                print(f"处理第 {current_group} 组")
                
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
                    print(f"解析错误: {line}, 错误: {e}")
    
    # 保存最后一个分组的状态
    if current_group > 0:
        cursor.execute('''
            INSERT OR REPLACE INTO group_status 
            (group_id, total_duration, total_segments, status)
            VALUES (?, ?, ?, 'available')
        ''', (current_group, group_total_duration, group_total_segments))
    
    conn.commit()
    conn.close()
    
    print(f"分组数据已导入完成，共处理 {current_group} 个分组")

def main():
    """
    主函数：创建数据库并导入分组数据
    """
    print("开始初始化分组分配数据库...")
    
    # 创建数据库
    create_group_assignment_database()
    
    # 导入分组数据
    parse_group_file_and_insert_data()
    
    print("分组分配数据库初始化完成！")

if __name__ == '__main__':
    main()