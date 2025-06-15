#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库服务
用于处理情感标注数据的数据库操作
"""

try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False
    print("警告: SQLite3 模块不可用，数据库功能将被禁用")

import os
import json
from datetime import datetime
from models.emotion_model import EmotionLabel
from utils.audio_utils import get_audio_duration
from utils.logger import emotion_logger
from config import Config

class DatabaseService:
    """数据库服务类"""
    
    @staticmethod
    def get_db_path():
        """获取数据库文件路径"""
        return os.path.join(Config.DATABASE_FOLDER, 'emotion_labels.db')
    
    @staticmethod
    def get_connection():
        """获取数据库连接"""
        if not SQLITE_AVAILABLE:
            raise Exception("SQLite3 模块不可用")
        
        db_path = DatabaseService.get_db_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        
        # 确保表存在
        DatabaseService._ensure_tables_exist(conn)
        
        return conn
    
    @staticmethod
    def _ensure_tables_exist(conn):
        """确保数据库表存在，如果不存在则创建"""
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='emotion_labels'
        """)
        
        if not cursor.fetchone():
            # 创建表
            cursor.execute('''
                CREATE TABLE emotion_labels (
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
            
            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_audio_speaker_user 
                ON emotion_labels(audio_file, speaker, username)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_username 
                ON emotion_labels(username)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_speaker 
                ON emotion_labels(speaker)
            ''')
            
            # 创建触发器用于更新 updated_at
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS update_emotion_labels_timestamp 
                AFTER UPDATE ON emotion_labels
                BEGIN
                    UPDATE emotion_labels SET updated_at = CURRENT_TIMESTAMP 
                    WHERE id = NEW.id;
                END
            ''')
            
            conn.commit()
            print("数据库表创建成功")
    
    @staticmethod
    def save_label(label_data, speaker, audio_file_path):
        """
        保存标注数据到数据库
        
        Args:
            label_data: 标注数据字典
            speaker: 说话人
            audio_file_path: 音频文件路径
            
        Returns:
            bool: 保存是否成功
        """
        conn = None
        try:
            from utils.audio_utils import get_audio_duration
            
            # 获取音频时长
            audio_duration = get_audio_duration(audio_file_path)
            
            # 创建标注对象
            label = EmotionLabel(
                audio_file=label_data.get("audio_file"),
                v_value=label_data.get("v_value"),
                a_value=label_data.get("a_value"),
                emotion_type=label_data.get("emotion_type"),
                discrete_emotion=label_data.get("discrete_emotion"),
                username=label_data.get("username"),
                patient_status=label_data.get("patient_status"),
                audio_duration=audio_duration
            )
            
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 插入或更新数据
            cursor.execute('''
                INSERT OR REPLACE INTO emotion_labels (
                    audio_file, speaker, username, v_value, a_value,
                    emotion_type, discrete_emotion, patient_status,
                    audio_duration, play_count, va_complete, discrete_complete,
                    timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                label.audio_file,
                speaker,
                label.username,
                label.v_value,
                label.a_value,
                label.emotion_type,
                label.discrete_emotion,
                label.patient_status,
                label.audio_duration,
                label.play_count,
                label.va_complete,
                label.discrete_complete,
                label.timestamp
            ))
            
            emotion_logger.log_database_operation(
                operation="INSERT OR REPLACE",
                table="emotion_labels",
                username=label.username,
                details={
                    "audio_file": label.audio_file,
                    "speaker": speaker,
                    "v_value": label.v_value,
                    "a_value": label.a_value,
                    "emotion_type": label.emotion_type,
                    "discrete_emotion": label.discrete_emotion
                },
                success=True
            )
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            emotion_logger.log_database_operation(
                operation="INSERT OR REPLACE",
                table="emotion_labels",
                username=label_data.get("username", "unknown"),
                details={"audio_file": label_data.get("audio_file"), "error": str(e)},
                success=False
            )
            print(f"保存标注数据时出错: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_label(username, speaker, filename):
        """
        获取标注数据
        
        Args:
            username: 用户名
            speaker: 说话人
            filename: 文件名
            
        Returns:
            dict: 标注数据字典，如果不存在则返回None
        """
        conn = None
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 处理分组说话人
            import re
            if re.match(r'spk\d+$', speaker):
                # 查询所有以该speaker开头的数据
                cursor.execute('''
                    SELECT * FROM emotion_labels 
                    WHERE username = ? AND speaker LIKE ? AND audio_file = ?
                ''', (username, f"{speaker}-%", filename))
            else:
                cursor.execute('''
                    SELECT * FROM emotion_labels 
                    WHERE username = ? AND speaker = ? AND audio_file = ?
                ''', (username, speaker, filename))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                # 将数据库行转换为字典
                label_dict = dict(row)
                
                # 计算标注完整性
                from models.emotion_model import calculate_annotation_completeness
                completeness = calculate_annotation_completeness(label_dict)
                label_dict['annotation_completeness'] = completeness
                
                emotion_logger.log_database_operation(
                    operation="SELECT",
                    table="emotion_labels",
                    username=username,
                    details={"audio_file": filename, "speaker": speaker, "found": True},
                    success=True
                )
                
                return label_dict
            
            emotion_logger.log_database_operation(
                operation="SELECT",
                table="emotion_labels",
                username=username,
                details={"audio_file": filename, "speaker": speaker, "found": False},
                success=True
            )
            
            return None
            
        except Exception as e:
            emotion_logger.log_database_operation(
                operation="SELECT",
                table="emotion_labels",
                username=username,
                details={"audio_file": filename, "speaker": speaker, "error": str(e)},
                success=False
            )
            print(f"获取标注数据时出错: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_labeled_files(username, speaker):
        """
        获取已标注的文件列表
        
        Args:
            username: 用户名
            speaker: 说话人
            
        Returns:
            tuple: (已标注文件集合, 标注完整性字典)
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 处理分组说话人
            import re
            if re.match(r'spk\d+$', speaker):
                # 查询所有以该speaker开头的数据
                cursor.execute('''
                    SELECT audio_file, v_value, a_value, emotion_type, 
                           discrete_emotion, patient_status, va_complete, discrete_complete
                    FROM emotion_labels 
                    WHERE username = ? AND speaker LIKE ?
                ''', (username, f"{speaker}-%"))
            else:
                cursor.execute('''
                    SELECT audio_file, v_value, a_value, emotion_type, 
                           discrete_emotion, patient_status, va_complete, discrete_complete
                    FROM emotion_labels 
                    WHERE username = ? AND speaker = ?
                ''', (username, speaker))
            
            rows = cursor.fetchall()
            conn.close()
            
            labeled_files = set()
            annotation_completeness = {}
            
            for row in rows:
                filename = row['audio_file']
                labeled_files.add(filename)
                
                # 计算标注完整性
                label_dict = dict(row)
                from models.emotion_model import calculate_annotation_completeness
                completeness = calculate_annotation_completeness(label_dict)
                annotation_completeness[filename] = completeness
            
            return labeled_files, annotation_completeness
            
        except Exception as e:
            print(f"获取已标注文件列表时出错: {e}")
            return set(), {}
    
    @staticmethod
    def update_play_count(username, speaker, filename):
        """
        更新音频播放次数
        
        Args:
            username: 用户名
            speaker: 说话人
            filename: 文件名
            
        Returns:
            int: 更新后的播放次数
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 处理分组说话人
            import re
            if re.match(r'spk\d+$', speaker):
                # 查找匹配的记录
                cursor.execute('''
                    SELECT speaker, play_count FROM emotion_labels 
                    WHERE username = ? AND audio_file = ? AND speaker LIKE ?
                ''', (username, filename, f"{speaker}-%"))
                
                row = cursor.fetchone()
                if row:
                    actual_speaker = row['speaker']
                    new_count = row['play_count'] + 1
                    
                    cursor.execute('''
                        UPDATE emotion_labels 
                        SET play_count = ? 
                        WHERE username = ? AND speaker = ? AND audio_file = ?
                    ''', (new_count, username, actual_speaker, filename))
                    
                    conn.commit()
                    conn.close()
                    return new_count
            else:
                cursor.execute('''
                    UPDATE emotion_labels 
                    SET play_count = play_count + 1 
                    WHERE username = ? AND speaker = ? AND audio_file = ?
                ''', (username, speaker, filename))
                
                if cursor.rowcount > 0:
                    # 获取更新后的播放次数
                    cursor.execute('''
                        SELECT play_count FROM emotion_labels 
                        WHERE username = ? AND speaker = ? AND audio_file = ?
                    ''', (username, speaker, filename))
                    
                    row = cursor.fetchone()
                    conn.commit()
                    conn.close()
                    return row['play_count'] if row else 1
            
            conn.close()
            return 0
            
        except Exception as e:
            print(f"更新播放次数时出错: {e}")
            return 0
    
    @staticmethod
    def get_play_count(username, speaker, filename):
        """
        获取音频播放次数
        
        Args:
            username: 用户名
            speaker: 说话人
            filename: 文件名
            
        Returns:
            int: 播放次数
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 处理分组说话人
            import re
            if re.match(r'spk\d+$', speaker):
                cursor.execute('''
                    SELECT play_count FROM emotion_labels 
                    WHERE username = ? AND audio_file = ? AND speaker LIKE ?
                ''', (username, filename, f"{speaker}-%"))
            else:
                cursor.execute('''
                    SELECT play_count FROM emotion_labels 
                    WHERE username = ? AND speaker = ? AND audio_file = ?
                ''', (username, speaker, filename))
            
            row = cursor.fetchone()
            conn.close()
            
            return row['play_count'] if row else 0
            
        except Exception as e:
            print(f"获取播放次数时出错: {e}")
            return 0
    
    @staticmethod
    def get_user_statistics(username):
        """
        获取用户标注统计信息
        
        Args:
            username: 用户名
            
        Returns:
            dict: 统计信息
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 总标注数量
            cursor.execute('''
                SELECT COUNT(*) as total_count FROM emotion_labels 
                WHERE username = ?
            ''', (username,))
            total_count = cursor.fetchone()['total_count']
            
            # VA完整标注数量
            cursor.execute('''
                SELECT COUNT(*) as va_complete_count FROM emotion_labels 
                WHERE username = ? AND va_complete = 1
            ''', (username,))
            va_complete_count = cursor.fetchone()['va_complete_count']
            
            # 离散情感完整标注数量
            cursor.execute('''
                SELECT COUNT(*) as discrete_complete_count FROM emotion_labels 
                WHERE username = ? AND discrete_complete = 1
            ''', (username,))
            discrete_complete_count = cursor.fetchone()['discrete_complete_count']
            
            # 按说话人统计
            cursor.execute('''
                SELECT speaker, COUNT(*) as count FROM emotion_labels 
                WHERE username = ? 
                GROUP BY speaker
                ORDER BY count DESC
            ''', (username,))
            speaker_stats = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_count': total_count,
                'va_complete_count': va_complete_count,
                'discrete_complete_count': discrete_complete_count,
                'speaker_stats': [dict(row) for row in speaker_stats]
            }
            
        except Exception as e:
            print(f"获取用户统计信息时出错: {e}")
            return {
                'total_count': 0,
                'va_complete_count': 0,
                'discrete_complete_count': 0,
                'speaker_stats': []
            }