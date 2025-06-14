#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库调试脚本
用于检查数据库状态和数据
"""

import sqlite3
import os
from config import Config

def check_database():
    """
    检查数据库状态
    """
    db_path = os.path.join(Config.DATABASE_FOLDER, 'emotion_labels.db')
    
    print(f"数据库路径: {db_path}")
    print(f"数据库文件存在: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("数据库文件不存在！")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"数据库中的表: {[table[0] for table in tables]}")
        
        # 检查emotion_labels表
        if ('emotion_labels',) in tables:
            cursor.execute("SELECT COUNT(*) FROM emotion_labels")
            count = cursor.fetchone()[0]
            print(f"emotion_labels表中的记录数: {count}")
            
            # 检查表结构
            cursor.execute("PRAGMA table_info(emotion_labels)")
            columns = cursor.fetchall()
            print("表结构:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
                
            # 显示前几条记录
            if count > 0:
                cursor.execute("SELECT * FROM emotion_labels LIMIT 3")
                records = cursor.fetchall()
                print("前3条记录:")
                for record in records:
                    print(f"  {record}")
        else:
            print("emotion_labels表不存在！")
            
        conn.close()
        
    except Exception as e:
        print(f"数据库检查出错: {e}")

if __name__ == '__main__':
    check_database()