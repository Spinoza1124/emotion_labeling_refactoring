# -*- coding: utf-8 -*-
"""
管理员服务
提供管理员后台管理功能的业务逻辑
"""

import os
import json
import csv
import sqlite3
import shutil
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any

from config import Config
from services.database_service import DatabaseService
from services.audio_service import AudioService
from group_assignment_manager import GroupAssignmentManager

class AdminService:
    """管理员服务类"""
    
    @staticmethod
    def get_system_overview() -> Dict[str, Any]:
        """
        获取系统概览统计信息
        
        Returns:
            Dict: 包含系统概览数据的字典
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 总用户数
            cursor.execute("SELECT COUNT(DISTINCT username) FROM emotion_labels")
            total_users = cursor.fetchone()[0]
            
            # 总音频文件数 - 直接统计emotion_annotation文件夹中的文件
            try:
                from utils.count_audio_files import update_audio_count_in_system
                total_audio_files = update_audio_count_in_system(verbose=False)
            except Exception as audio_error:
                # 如果音频文件夹不存在或统计失败，设为0
                total_audio_files = 0
                print(f"音频文件统计失败: {audio_error}")
            
            # 总标注数
            cursor.execute("SELECT COUNT(*) FROM emotion_labels")
            total_annotations = cursor.fetchone()[0]
            
            # 完成的标注数（VA和离散情感都完成）
            cursor.execute("""
                SELECT COUNT(*) FROM emotion_labels 
                WHERE va_complete = 1 AND discrete_complete = 1
            """)
            completed_annotations = cursor.fetchone()[0]
            
            # 今日新增标注数
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT COUNT(*) FROM emotion_labels 
                WHERE DATE(timestamp) = ?
            """, (today,))
            today_annotations = cursor.fetchone()[0]
            
            # 活跃用户数（最近7天有标注活动）
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT COUNT(DISTINCT username) FROM emotion_labels 
                WHERE DATE(timestamp) >= ?
            """, (week_ago,))
            active_users = cursor.fetchone()[0]
            
            conn.close()
            
            # 计算完成率
            completion_rate = (completed_annotations / total_annotations * 100) if total_annotations > 0 else 0
            
            return {
                "total_users": total_users,
                "total_audio_files": total_audio_files,
                "total_annotations": total_annotations,
                "completed_annotations": completed_annotations,
                "completion_rate": round(completion_rate, 2),
                "today_annotations": today_annotations,
                "active_users": active_users,
                "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            raise Exception(f"获取系统概览失败: {str(e)}")
    
    @staticmethod
    def get_users_statistics() -> List[Dict[str, Any]]:
        """
        获取所有用户的标注统计信息
        
        Returns:
            List: 包含用户统计信息的列表
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 获取每个用户的统计信息
            cursor.execute("""
                SELECT 
                    username,
                    COUNT(*) as user_annotations,
                    SUM(CASE WHEN va_complete = 1 AND discrete_complete = 1 THEN 1 ELSE 0 END) as completed_annotations,
                    COUNT(DISTINCT speaker) as speakers_count,
                    AVG(play_count) as avg_play_count,
                    MIN(timestamp) as first_annotation,
                    MAX(timestamp) as last_annotation
                FROM emotion_labels 
                GROUP BY username
                ORDER BY user_annotations DESC
            """)
            
            users_data = []
            group_manager = GroupAssignmentManager()
            
            for row in cursor.fetchall():
                username = row[0]
                user_annotations = row[1]
                completed_annotations = row[2]
                
                # 获取用户的组分配信息
                try:
                    assignment_info = group_manager.get_user_assignment_info(username)
                    if assignment_info and assignment_info.get('group_info'):
                        # 使用组的总样本数作为"总标注数"
                        total_annotations = assignment_info['group_info'].get('total_segments', user_annotations)
                        # 重新计算完成率：用户完成数 / 组总样本数
                        completion_rate = (completed_annotations / total_annotations * 100) if total_annotations > 0 else 0
                    else:
                        # 如果用户没有分配组，使用用户实际标注数
                        total_annotations = user_annotations
                        completion_rate = (completed_annotations / total_annotations * 100) if total_annotations > 0 else 0
                except Exception:
                    # 如果获取组信息失败，使用用户实际标注数
                    total_annotations = user_annotations
                    completion_rate = (completed_annotations / total_annotations * 100) if total_annotations > 0 else 0
                
                users_data.append({
                    "username": username,
                    "total_annotations": total_annotations,
                    "completed_annotations": completed_annotations,
                    "completion_rate": round(completion_rate, 2),
                    "speakers_count": row[3],
                    "avg_play_count": round(row[4], 2) if row[4] else 0,
                    "first_annotation": row[5],
                    "last_annotation": row[6]
                })
            
            conn.close()
            return users_data
            
        except Exception as e:
            raise Exception(f"获取用户统计失败: {str(e)}")
    
    @staticmethod
    def get_user_details(username: str) -> Dict[str, Any]:
        """
        获取指定用户的详细标注信息
        
        Args:
            username (str): 用户名
            
        Returns:
            Dict: 用户详细信息
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 用户基本信息
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_annotations,
                    SUM(CASE WHEN va_complete = 1 AND discrete_complete = 1 THEN 1 ELSE 0 END) as completed_annotations,
                    COUNT(DISTINCT speaker) as speakers_count,
                    SUM(audio_duration) as total_duration,
                    AVG(play_count) as avg_play_count,
                    MIN(timestamp) as first_annotation,
                    MAX(timestamp) as last_annotation
                FROM emotion_labels 
                WHERE username = ?
            """, (username,))
            
            user_info = cursor.fetchone()
            
            # 按说话人分组的统计
            cursor.execute("""
                SELECT 
                    speaker,
                    COUNT(*) as annotations_count,
                    SUM(CASE WHEN va_complete = 1 AND discrete_complete = 1 THEN 1 ELSE 0 END) as completed_count
                FROM emotion_labels 
                WHERE username = ?
                GROUP BY speaker
                ORDER BY annotations_count DESC
            """, (username,))
            
            speakers_stats = []
            for row in cursor.fetchall():
                completion_rate = (row[2] / row[1] * 100) if row[1] > 0 else 0
                speakers_stats.append({
                    "speaker": row[0],
                    "annotations_count": row[1],
                    "completed_count": row[2],
                    "completion_rate": round(completion_rate, 2)
                })
            
            # 最近的标注记录
            cursor.execute("""
                SELECT audio_file, speaker, va_complete, discrete_complete, timestamp
                FROM emotion_labels 
                WHERE username = ?
                ORDER BY timestamp DESC
                LIMIT 10
            """, (username,))
            
            recent_annotations = []
            for row in cursor.fetchall():
                recent_annotations.append({
                    "audio_file": row[0],
                    "speaker": row[1],
                    "va_complete": bool(row[2]),
                    "discrete_complete": bool(row[3]),
                    "timestamp": row[4]
                })
            
            conn.close()
            
            completion_rate = (user_info[1] / user_info[0] * 100) if user_info[0] > 0 else 0
            
            return {
                "username": username,
                "total_annotations": user_info[0],
                "completed_annotations": user_info[1],
                "completion_rate": round(completion_rate, 2),
                "speakers_count": user_info[2],
                "total_duration": round(user_info[3], 2) if user_info[3] else 0,
                "avg_play_count": round(user_info[4], 2) if user_info[4] else 0,
                "first_annotation": user_info[5],
                "last_annotation": user_info[6],
                "speakers_stats": speakers_stats,
                "recent_annotations": recent_annotations
            }
            
        except Exception as e:
            raise Exception(f"获取用户详细信息失败: {str(e)}")
    
    @staticmethod
    def get_speakers_statistics() -> List[Dict[str, Any]]:
        """
        获取所有说话人的标注统计
        
        Returns:
            List: 说话人统计信息列表
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    speaker,
                    COUNT(*) as total_annotations,
                    SUM(CASE WHEN va_complete = 1 AND discrete_complete = 1 THEN 1 ELSE 0 END) as completed_annotations,
                    COUNT(DISTINCT username) as annotators_count,
                    COUNT(DISTINCT audio_file) as audio_files_count,
                    SUM(audio_duration) as total_duration
                FROM emotion_labels 
                GROUP BY speaker
                ORDER BY total_annotations DESC
            """)
            
            speakers_data = []
            for row in cursor.fetchall():
                completion_rate = (row[2] / row[1] * 100) if row[1] > 0 else 0
                
                speakers_data.append({
                    "speaker": row[0],
                    "total_annotations": row[1],
                    "completed_annotations": row[2],
                    "completion_rate": round(completion_rate, 2),
                    "annotators_count": row[3],
                    "audio_files_count": row[4],
                    "total_duration": round(row[5], 2) if row[5] else 0
                })
            
            conn.close()
            return speakers_data
            
        except Exception as e:
            raise Exception(f"获取说话人统计失败: {str(e)}")
    
    @staticmethod
    def get_annotation_progress() -> Dict[str, Any]:
        """
        获取标注进度统计
        
        Returns:
            Dict: 标注进度信息
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 按日期统计标注进度
            cursor.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as daily_annotations,
                    SUM(CASE WHEN va_complete = 1 AND discrete_complete = 1 THEN 1 ELSE 0 END) as daily_completed
                FROM emotion_labels 
                WHERE DATE(timestamp) >= DATE('now', '-30 days')
                GROUP BY DATE(timestamp)
                ORDER BY date
            """)
            
            daily_progress = []
            for row in cursor.fetchall():
                daily_progress.append({
                    "date": row[0],
                    "annotations": row[1],
                    "completed": row[2]
                })
            
            # 按用户统计本周进度
            cursor.execute("""
                SELECT 
                    username,
                    COUNT(*) as week_annotations,
                    SUM(CASE WHEN va_complete = 1 AND discrete_complete = 1 THEN 1 ELSE 0 END) as week_completed
                FROM emotion_labels 
                WHERE DATE(timestamp) >= DATE('now', '-7 days')
                GROUP BY username
                ORDER BY week_annotations DESC
            """)
            
            weekly_user_progress = []
            for row in cursor.fetchall():
                weekly_user_progress.append({
                    "username": row[0],
                    "annotations": row[1],
                    "completed": row[2]
                })
            
            conn.close()
            
            return {
                "daily_progress": daily_progress,
                "weekly_user_progress": weekly_user_progress
            }
            
        except Exception as e:
            raise Exception(f"获取标注进度失败: {str(e)}")
    
    @staticmethod
    def get_annotation_quality() -> Dict[str, Any]:
        """
        获取标注质量分析
        
        Returns:
            Dict: 标注质量分析数据
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 播放次数分布（质量指标之一）
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN play_count = 0 THEN '0次'
                        WHEN play_count = 1 THEN '1次'
                        WHEN play_count BETWEEN 2 AND 3 THEN '2-3次'
                        WHEN play_count BETWEEN 4 AND 5 THEN '4-5次'
                        ELSE '5次以上'
                    END as play_range,
                    COUNT(*) as count
                FROM emotion_labels
                GROUP BY play_range
            """)
            
            play_count_distribution = []
            for row in cursor.fetchall():
                play_count_distribution.append({
                    "range": row[0],
                    "count": row[1]
                })
            
            # 情感类型分布
            cursor.execute("""
                SELECT 
                    emotion_type,
                    COUNT(*) as count
                FROM emotion_labels
                WHERE emotion_type IS NOT NULL
                GROUP BY emotion_type
            """)
            
            emotion_type_distribution = []
            for row in cursor.fetchall():
                emotion_type_distribution.append({
                    "type": row[0],
                    "count": row[1]
                })
            
            # 离散情感分布
            cursor.execute("""
                SELECT 
                    discrete_emotion,
                    COUNT(*) as count
                FROM emotion_labels
                WHERE discrete_emotion IS NOT NULL
                GROUP BY discrete_emotion
                ORDER BY count DESC
            """)
            
            discrete_emotion_distribution = []
            for row in cursor.fetchall():
                discrete_emotion_distribution.append({
                    "emotion": row[0],
                    "count": row[1]
                })
            
            # 标注时间分析（从创建到完成的时间）
            cursor.execute("""
                SELECT 
                    username,
                    AVG(JULIANDAY(updated_at) - JULIANDAY(timestamp)) * 24 * 60 as avg_annotation_time_minutes
                FROM emotion_labels
                WHERE va_complete = 1 AND discrete_complete = 1
                GROUP BY username
            """)
            
            annotation_time_by_user = []
            for row in cursor.fetchall():
                annotation_time_by_user.append({
                    "username": row[0],
                    "avg_time_minutes": round(row[1], 2) if row[1] else 0
                })
            
            conn.close()
            
            return {
                "play_count_distribution": play_count_distribution,
                "emotion_type_distribution": emotion_type_distribution,
                "discrete_emotion_distribution": discrete_emotion_distribution,
                "annotation_time_by_user": annotation_time_by_user
            }
            
        except Exception as e:
            raise Exception(f"获取标注质量分析失败: {str(e)}")
    
    @staticmethod
    def export_annotation_data(format='csv', username=None, speaker=None) -> Dict[str, Any]:
        """
        导出标注数据
        
        Args:
            format (str): 导出格式 ('csv' 或 'json')
            username (str, optional): 指定用户名
            speaker (str, optional): 指定说话人
            
        Returns:
            Dict: 导出结果信息
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 构建查询条件
            where_conditions = []
            params = []
            
            if username:
                where_conditions.append("username = ?")
                params.append(username)
            
            if speaker:
                where_conditions.append("speaker = ?")
                params.append(speaker)
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # 查询数据
            query = f"""
                SELECT 
                    audio_file, speaker, username, v_value, a_value, 
                    emotion_type, discrete_emotion, patient_status,
                    audio_duration, play_count, va_complete, discrete_complete,
                    timestamp, updated_at
                FROM emotion_labels
                {where_clause}
                ORDER BY timestamp
            """
            
            cursor.execute(query, params)
            data = cursor.fetchall()
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename_parts = ['emotion_labels', timestamp]
            if username:
                filename_parts.insert(-1, f'user_{username}')
            if speaker:
                filename_parts.insert(-1, f'speaker_{speaker}')
            
            filename = '_'.join(filename_parts)
            
            # 确保导出目录存在
            export_dir = os.path.join(Config.DATABASE_FOLDER, 'exports')
            os.makedirs(export_dir, exist_ok=True)
            
            if format.lower() == 'csv':
                filepath = os.path.join(export_dir, f'{filename}.csv')
                
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # 写入表头
                    headers = [
                        '音频文件', '说话人', '用户名', 'V值', 'A值',
                        '情感类型', '离散情感', '患者状态',
                        '音频时长', '播放次数', 'VA完成', '离散完成',
                        '创建时间', '更新时间'
                    ]
                    writer.writerow(headers)
                    
                    # 写入数据
                    for row in data:
                        writer.writerow(row)
                        
            elif format.lower() == 'json':
                filepath = os.path.join(export_dir, f'{filename}.json')
                
                json_data = []
                for row in data:
                    json_data.append({
                        'audio_file': row[0],
                        'speaker': row[1],
                        'username': row[2],
                        'v_value': row[3],
                        'a_value': row[4],
                        'emotion_type': row[5],
                        'discrete_emotion': row[6],
                        'patient_status': row[7],
                        'audio_duration': row[8],
                        'play_count': row[9],
                        'va_complete': bool(row[10]),
                        'discrete_complete': bool(row[11]),
                        'timestamp': row[12],
                        'updated_at': row[13]
                    })
                
                with open(filepath, 'w', encoding='utf-8') as jsonfile:
                    json.dump(json_data, jsonfile, ensure_ascii=False, indent=2)
            
            else:
                raise ValueError(f"不支持的导出格式: {format}")
            
            conn.close()
            
            return {
                "success": True,
                "message": "数据导出成功",
                "filename": os.path.basename(filepath),
                "filepath": filepath,
                "record_count": len(data),
                "export_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            raise Exception(f"导出数据失败: {str(e)}")
    
    @staticmethod
    def reset_user_progress(username: str) -> Dict[str, Any]:
        """
        重置用户标注进度
        
        Args:
            username (str): 用户名
            
        Returns:
            Dict: 重置结果
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 获取要删除的记录数
            cursor.execute("SELECT COUNT(*) FROM emotion_labels WHERE username = ?", (username,))
            record_count = cursor.fetchone()[0]
            
            # 删除用户的所有标注记录
            cursor.execute("DELETE FROM emotion_labels WHERE username = ?", (username,))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": f"已重置用户 {username} 的标注进度",
                "deleted_records": record_count
            }
            
        except Exception as e:
            raise Exception(f"重置用户进度失败: {str(e)}")
    
    @staticmethod
    def backup_database() -> Dict[str, Any]:
        """
        备份数据库
        
        Returns:
            Dict: 备份结果
        """
        try:
            # 创建备份目录
            backup_dir = os.path.join(Config.DATABASE_FOLDER, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成备份文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'emotion_labels_backup_{timestamp}.db'
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # 复制数据库文件
            source_db = DatabaseService.get_db_path()
            shutil.copy2(source_db, backup_path)
            
            # 获取备份文件大小
            backup_size = os.path.getsize(backup_path)
            
            return {
                "success": True,
                "message": "数据库备份成功",
                "backup_filename": backup_filename,
                "backup_path": backup_path,
                "backup_size": backup_size,
                "backup_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            raise Exception(f"数据库备份失败: {str(e)}")
    
    @staticmethod
    def get_system_status() -> Dict[str, Any]:
        """
        获取系统状态信息
        
        Returns:
            Dict: 系统状态信息
        """
        try:
            # 数据库状态
            db_path = DatabaseService.get_db_path()
            db_exists = os.path.exists(db_path)
            db_size = os.path.getsize(db_path) if db_exists else 0
            
            # 音频文件夹状态
            audio_folder_exists = os.path.exists(Config.AUDIO_FOLDER)
            
            # 数据库连接测试
            try:
                conn = DatabaseService.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM emotion_labels")
                db_accessible = True
                total_records = cursor.fetchone()[0]
                conn.close()
            except:
                db_accessible = False
                total_records = 0
            
            # 磁盘空间检查
            import shutil as disk_util
            total, used, free = disk_util.disk_usage(Config.DATABASE_FOLDER)
            
            return {
                "database": {
                    "exists": db_exists,
                    "accessible": db_accessible,
                    "size_bytes": db_size,
                    "size_mb": round(db_size / 1024 / 1024, 2),
                    "total_records": total_records
                },
                "audio_folder": {
                    "exists": audio_folder_exists,
                    "path": Config.AUDIO_FOLDER
                },
                "disk_space": {
                    "total_gb": round(total / 1024 / 1024 / 1024, 2),
                    "used_gb": round(used / 1024 / 1024 / 1024, 2),
                    "free_gb": round(free / 1024 / 1024 / 1024, 2),
                    "usage_percent": round(used / total * 100, 2)
                },
                "check_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            raise Exception(f"获取系统状态失败: {str(e)}")