#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理脚本
用于查看和管理情感标注数据库
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import sqlite3
except ImportError:
    print("SQLite3 模块不可用")
    sys.exit(1)

from config import Config

def get_db_connection():
    """获取数据库连接"""
    db_path = os.path.join(Config.DATABASE_FOLDER, 'emotion_labels.db')
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return None
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def show_table_info():
    """显示表结构信息"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # 获取表结构
        cursor.execute("PRAGMA table_info(emotion_labels)")
        columns = cursor.fetchall()
        
        print("\n=== 表结构信息 ===")
        print(f"{'列名':<20} {'类型':<15} {'非空':<5} {'默认值':<15}")
        print("-" * 60)
        for col in columns:
            print(f"{col['name']:<20} {col['type']:<15} {col['notnull']:<5} {col['dflt_value'] or '':<15}")
        
        # 获取记录总数
        cursor.execute("SELECT COUNT(*) as count FROM emotion_labels")
        count = cursor.fetchone()['count']
        print(f"\n总记录数: {count}")
        
    except Exception as e:
        print(f"查询表信息时出错: {e}")
    finally:
        conn.close()

def show_recent_labels(limit=10):
    """显示最近的标注记录"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT audio_file, speaker, username, emotion_type, 
                   patient_status, timestamp, updated_at
            FROM emotion_labels 
            ORDER BY updated_at DESC 
            LIMIT ?
        """, (limit,))
        
        records = cursor.fetchall()
        
        print(f"\n=== 最近 {limit} 条标注记录 ===")
        if not records:
            print("暂无记录")
            return
        
        print(f"{'音频文件':<25} {'说话人':<10} {'用户':<10} {'情感类型':<10} {'患者状态':<10} {'更新时间':<20}")
        print("-" * 100)
        
        for record in records:
            print(f"{record['audio_file']:<25} {record['speaker']:<10} {record['username']:<10} "
                  f"{record['emotion_type'] or 'N/A':<10} {record['patient_status'] or 'N/A':<10} "
                  f"{record['updated_at']:<20}")
        
    except Exception as e:
        print(f"查询记录时出错: {e}")
    finally:
        conn.close()

def show_user_stats():
    """显示用户统计信息"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, 
                   COUNT(*) as total_labels,
                   SUM(CASE WHEN v_value IS NOT NULL AND a_value IS NOT NULL THEN 1 ELSE 0 END) as va_complete,
                   SUM(CASE WHEN emotion_type IS NOT NULL THEN 1 ELSE 0 END) as emotion_complete,
                   SUM(play_count) as total_plays
            FROM emotion_labels 
            GROUP BY username
            ORDER BY total_labels DESC
        """)
        
        records = cursor.fetchall()
        
        print("\n=== 用户统计信息 ===")
        if not records:
            print("暂无用户数据")
            return
        
        print(f"{'用户名':<15} {'总标注数':<10} {'VA完整':<10} {'情感完整':<10} {'总播放次数':<12}")
        print("-" * 70)
        
        for record in records:
            print(f"{record['username']:<15} {record['total_labels']:<10} "
                  f"{record['va_complete']:<10} {record['emotion_complete']:<10} "
                  f"{record['total_plays']:<12}")
        
    except Exception as e:
        print(f"查询统计信息时出错: {e}")
    finally:
        conn.close()

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 manage_db.py info     - 显示表结构信息")
        print("  python3 manage_db.py recent   - 显示最近的标注记录")
        print("  python3 manage_db.py stats    - 显示用户统计信息")
        return
    
    command = sys.argv[1]
    
    if command == "info":
        show_table_info()
    elif command == "recent":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        show_recent_labels(limit)
    elif command == "stats":
        show_user_stats()
    else:
        print(f"未知命令: {command}")

if __name__ == "__main__":
    main()