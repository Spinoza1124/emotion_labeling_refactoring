#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分组分配管理器
负责管理用户分组分配、进度跟踪等功能
"""

import sqlite3
import os
from datetime import datetime
from config import Config

class GroupAssignmentManager:
    def __init__(self):
        self.db_path = os.path.join(Config.DATABASE_FOLDER, 'group_assignments.db')
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """确保数据库存在"""
        if not os.path.exists(self.db_path):
            print(f"分组分配数据库不存在，请先运行初始化脚本")
            return False
        return True
    
    def get_available_group_for_user(self, username):
        """
        为用户获取可用的分组
        返回: (group_id, group_info) 或 None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查用户是否已经有分配的分组
            cursor.execute('''
                SELECT group_id, status FROM group_assignments 
                WHERE username = ? AND status IN ('assigned', 'in_progress')
            ''', (username,))
            
            existing_assignment = cursor.fetchone()
            if existing_assignment:
                group_id, status = existing_assignment
                # 获取分组详细信息
                group_info = self.get_group_info(group_id)
                return group_id, group_info
            
            # 查找可用的分组（分配人数少于3人的分组）
            cursor.execute('''
                SELECT gs.group_id, gs.total_duration, gs.total_segments, 
                       COUNT(ga.username) as assigned_count
                FROM group_status gs
                LEFT JOIN group_assignments ga ON gs.group_id = ga.group_id
                WHERE gs.status = 'available'
                GROUP BY gs.group_id
                HAVING assigned_count < 3
                ORDER BY gs.group_id
                LIMIT 1
            ''')
            
            result = cursor.fetchone()
            if result:
                group_id, total_duration, total_segments, assigned_count = result
                return group_id, {
                    'total_duration': total_duration,
                    'total_segments': total_segments,
                    'assigned_count': assigned_count
                }
            
            return None, None
            
        finally:
            conn.close()
    
    def assign_group_to_user(self, username, group_id):
        """
        将分组分配给用户
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查分组是否还有空位
            cursor.execute('''
                SELECT COUNT(*) FROM group_assignments 
                WHERE group_id = ?
            ''', (group_id,))
            
            current_count = cursor.fetchone()[0]
            if current_count >= 3:
                return False, "该分组已满员"
            
            # 获取分组的总段数
            cursor.execute('''
                SELECT total_segments FROM group_status 
                WHERE group_id = ?
            ''', (group_id,))
            
            total_segments = cursor.fetchone()[0]
            
            # 分配分组给用户
            cursor.execute('''
                INSERT OR REPLACE INTO group_assignments 
                (group_id, username, status, total_segments)
                VALUES (?, ?, 'assigned', ?)
            ''', (group_id, username, total_segments))
            
            # 更新分组状态表的分配计数
            cursor.execute('''
                UPDATE group_status 
                SET assigned_count = assigned_count + 1,
                    status = CASE 
                        WHEN assigned_count + 1 >= 3 THEN 'in_progress'
                        ELSE 'available'
                    END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE group_id = ?
            ''', (group_id,))
            
            conn.commit()
            return True, "分组分配成功"
            
        except Exception as e:
            conn.rollback()
            return False, f"分配失败: {str(e)}"
        finally:
            conn.close()
    
    def get_group_info(self, group_id):
        """
        获取分组详细信息
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 获取分组基本信息
            cursor.execute('''
                SELECT total_duration, total_segments, assigned_count, status
                FROM group_status 
                WHERE group_id = ?
            ''', (group_id,))
            
            group_basic = cursor.fetchone()
            if not group_basic:
                return None
            
            # 获取分组中的说话人信息
            cursor.execute('''
                SELECT speaker_id, duration, segment_count
                FROM speaker_groups 
                WHERE group_id = ?
                ORDER BY duration DESC
            ''', (group_id,))
            
            speakers = cursor.fetchall()
            
            return {
                'group_id': group_id,
                'total_duration': group_basic[0],
                'total_segments': group_basic[1],
                'assigned_count': group_basic[2],
                'status': group_basic[3],
                'speakers': [{
                    'speaker_id': speaker[0],
                    'duration': speaker[1],
                    'segment_count': speaker[2]
                } for speaker in speakers]
            }
            
        finally:
            conn.close()
    
    def get_user_assignment_info(self, username):
        """
        获取用户的分组分配信息
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT ga.group_id, ga.status, ga.progress_count, ga.total_segments,
                       ga.assigned_at, ga.completed_at
                FROM group_assignments ga
                WHERE ga.username = ?
            ''', (username,))
            
            assignment = cursor.fetchone()
            if not assignment:
                return None
            
            group_id, status, progress_count, total_segments, assigned_at, completed_at = assignment
            
            # 获取分组详细信息
            group_info = self.get_group_info(group_id)
            
            return {
                'group_id': group_id,
                'status': status,
                'progress_count': progress_count,
                'total_segments': total_segments,
                'assigned_at': assigned_at,
                'completed_at': completed_at,
                'group_info': group_info
            }
            
        finally:
            conn.close()
    
    def update_user_progress(self, username, group_id, progress_count):
        """
        更新用户标注进度
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE group_assignments 
                SET progress_count = ?,
                    status = CASE 
                        WHEN progress_count >= total_segments THEN 'completed'
                        ELSE 'in_progress'
                    END,
                    completed_at = CASE 
                        WHEN progress_count >= total_segments THEN CURRENT_TIMESTAMP
                        ELSE completed_at
                    END
                WHERE username = ? AND group_id = ?
            ''', (progress_count, username, group_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"更新进度失败: {e}")
            return False
        finally:
            conn.close()
    
    def get_group_speakers(self, group_id):
        """
        获取分组中的所有说话人ID列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT speaker_id FROM speaker_groups 
                WHERE group_id = ?
                ORDER BY speaker_id
            ''', (group_id,))
            
            speakers = cursor.fetchall()
            return [speaker[0] for speaker in speakers]
            
        finally:
            conn.close()
    
    def get_all_groups_status(self):
        """
        获取所有分组的状态信息
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT gs.group_id, gs.total_duration, gs.total_segments, 
                       gs.assigned_count, gs.completed_count, gs.status,
                       COUNT(ga.username) as actual_assigned
                FROM group_status gs
                LEFT JOIN group_assignments ga ON gs.group_id = ga.group_id
                GROUP BY gs.group_id
                ORDER BY gs.group_id
            ''')
            
            groups = cursor.fetchall()
            return [{
                'group_id': group[0],
                'total_duration': group[1],
                'total_segments': group[2],
                'assigned_count': group[3],
                'completed_count': group[4],
                'status': group[5],
                'actual_assigned': group[6]
            } for group in groups]
            
        finally:
            conn.close()