#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理员数据模型
提供管理员用户的数据库操作功能，支持超级管理员和普通管理员的分层管理
"""

import os
import sqlite3
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from config import Config
from utils.logger import emotion_logger

class AdminModel:
    """管理员数据模型类"""
    
    # 管理员角色常量
    ROLE_SUPER_ADMIN = 'super_admin'  # 超级管理员
    ROLE_ADMIN = 'admin'              # 普通管理员
    
    def __init__(self):
        """
        初始化管理员模型
        """
        self.db_path = os.path.join(Config.DATABASE_FOLDER, 'admins.db')
        self.init_database()
    
    def init_database(self):
        """
        初始化管理员数据库表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建管理员表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'admin',
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    description TEXT
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_admin_username ON admins(username)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_admin_role ON admins(role)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_admin_active ON admins(is_active)')
            
            conn.commit()
            
            # 检查是否存在超级管理员，如果不存在则创建默认的
            self._ensure_super_admin_exists(cursor)
            
            conn.commit()
            conn.close()
            
            emotion_logger.log_system_event("管理员数据库初始化完成")
            
        except Exception as e:
            emotion_logger.log_error(e, "管理员数据库初始化失败")
            raise
    
    def _ensure_super_admin_exists(self, cursor):
        """
        确保存在至少一个超级管理员
        
        Args:
            cursor: 数据库游标
        """
        cursor.execute('SELECT COUNT(*) FROM admins WHERE role = ?', (self.ROLE_SUPER_ADMIN,))
        super_admin_count = cursor.fetchone()[0]
        
        if super_admin_count == 0:
            # 创建默认超级管理员
            default_password = 'admin123'
            password_hash = self._hash_password(default_password)
            
            cursor.execute('''
                INSERT INTO admins (username, password_hash, role, description)
                VALUES (?, ?, ?, ?)
            ''', (
                'admin',
                password_hash,
                self.ROLE_SUPER_ADMIN,
                '系统默认超级管理员'
            ))
            
            emotion_logger.log_system_event(
                "创建默认超级管理员",
                {"username": "admin", "role": self.ROLE_SUPER_ADMIN}
            )
    
    def _hash_password(self, password: str) -> str:
        """
        对密码进行哈希加密
        
        Args:
            password (str): 原始密码
            
        Returns:
            str: 加密后的密码哈希
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def verify_admin(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        验证管理员登录信息
        
        Args:
            username (str): 用户名
            password (str): 密码
            
        Returns:
            Optional[Dict]: 验证成功返回管理员信息，失败返回None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self._hash_password(password)
            
            cursor.execute('''
                SELECT id, username, role, created_by, created_at, last_login, description
                FROM admins 
                WHERE username = ? AND password_hash = ? AND is_active = 1
            ''', (username, password_hash))
            
            admin = cursor.fetchone()
            
            if admin:
                # 更新最后登录时间
                cursor.execute(
                    'UPDATE admins SET last_login = ? WHERE id = ?',
                    (datetime.now().isoformat(), admin[0])
                )
                conn.commit()
                
                admin_info = {
                    'id': admin[0],
                    'username': admin[1],
                    'role': admin[2],
                    'created_by': admin[3],
                    'created_at': admin[4],
                    'last_login': admin[5],
                    'description': admin[6]
                }
                
                emotion_logger.log_user_activity(
                    username=username,
                    action="管理员登录成功",
                    details={"role": admin[2]}
                )
                
                conn.close()
                return admin_info
            else:
                emotion_logger.log_user_activity(
                    username=username,
                    action="管理员登录失败",
                    details={"reason": "用户名或密码错误"}
                )
                conn.close()
                return None
                
        except Exception as e:
            emotion_logger.log_error(e, "管理员验证失败", username)
            return None
    
    def create_admin(self, username: str, password: str, role: str, created_by: str, description: str = None) -> bool:
        """
        创建新管理员
        
        Args:
            username (str): 用户名
            password (str): 密码
            role (str): 角色 (admin 或 super_admin)
            created_by (str): 创建者用户名
            description (str): 描述信息
            
        Returns:
            bool: 创建成功返回True，失败返回False
        """
        try:
            # 验证角色
            if role not in [self.ROLE_ADMIN, self.ROLE_SUPER_ADMIN]:
                emotion_logger.log_error(f"无效的管理员角色: {role}", "创建管理员", created_by)
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查用户名是否已存在
            cursor.execute('SELECT COUNT(*) FROM admins WHERE username = ?', (username,))
            if cursor.fetchone()[0] > 0:
                emotion_logger.log_error(f"管理员用户名已存在: {username}", "创建管理员", created_by)
                conn.close()
                return False
            
            password_hash = self._hash_password(password)
            
            cursor.execute('''
                INSERT INTO admins (username, password_hash, role, created_by, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, role, created_by, description))
            
            conn.commit()
            conn.close()
            
            emotion_logger.log_user_activity(
                username=created_by,
                action="创建管理员",
                details={
                    "new_admin_username": username,
                    "new_admin_role": role,
                    "description": description
                }
            )
            
            return True
            
        except Exception as e:
            emotion_logger.log_error(e, "创建管理员失败", created_by)
            return False
    
    def get_all_admins(self) -> List[Dict[str, Any]]:
        """
        获取所有管理员列表
        
        Returns:
            List[Dict]: 管理员信息列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, role, created_by, created_at, last_login, is_active, description
                FROM admins 
                ORDER BY created_at DESC
            ''')
            
            admins = cursor.fetchall()
            conn.close()
            
            return [{
                'id': admin[0],
                'username': admin[1],
                'role': admin[2],
                'created_by': admin[3],
                'created_at': admin[4],
                'last_login': admin[5],
                'is_active': bool(admin[6]),
                'description': admin[7]
            } for admin in admins]
            
        except Exception as e:
            emotion_logger.log_error(e, "获取管理员列表失败")
            return []
    
    def update_admin_status(self, admin_id: int, is_active: bool, operator: str) -> bool:
        """
        更新管理员状态（启用/禁用）
        
        Args:
            admin_id (int): 管理员ID
            is_active (bool): 是否启用
            operator (str): 操作者用户名
            
        Returns:
            bool: 更新成功返回True，失败返回False
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取管理员信息
            cursor.execute('SELECT username, role FROM admins WHERE id = ?', (admin_id,))
            admin_info = cursor.fetchone()
            
            if not admin_info:
                emotion_logger.log_error(f"管理员不存在: ID {admin_id}", "更新管理员状态", operator)
                conn.close()
                return False
            
            # 不能禁用超级管理员
            if admin_info[1] == self.ROLE_SUPER_ADMIN and not is_active:
                emotion_logger.log_error("不能禁用超级管理员", "更新管理员状态", operator)
                conn.close()
                return False
            
            cursor.execute(
                'UPDATE admins SET is_active = ? WHERE id = ?',
                (is_active, admin_id)
            )
            
            conn.commit()
            conn.close()
            
            emotion_logger.log_user_activity(
                username=operator,
                action="更新管理员状态",
                details={
                    "target_admin": admin_info[0],
                    "new_status": "启用" if is_active else "禁用"
                }
            )
            
            return True
            
        except Exception as e:
            emotion_logger.log_error(e, "更新管理员状态失败", operator)
            return False
    
    def delete_admin(self, admin_id: int, operator: str) -> bool:
        """
        删除管理员
        
        Args:
            admin_id (int): 管理员ID
            operator (str): 操作者用户名
            
        Returns:
            bool: 删除成功返回True，失败返回False
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取管理员信息
            cursor.execute('SELECT username, role FROM admins WHERE id = ?', (admin_id,))
            admin_info = cursor.fetchone()
            
            if not admin_info:
                emotion_logger.log_error(f"管理员不存在: ID {admin_id}", "删除管理员", operator)
                conn.close()
                return False
            
            # 不能删除超级管理员
            if admin_info[1] == self.ROLE_SUPER_ADMIN:
                emotion_logger.log_error("不能删除超级管理员", "删除管理员", operator)
                conn.close()
                return False
            
            cursor.execute('DELETE FROM admins WHERE id = ?', (admin_id,))
            
            conn.commit()
            conn.close()
            
            emotion_logger.log_user_activity(
                username=operator,
                action="删除管理员",
                details={"deleted_admin": admin_info[0]}
            )
            
            return True
            
        except Exception as e:
            emotion_logger.log_error(e, "删除管理员失败", operator)
            return False
    
    def change_password(self, admin_id: int, new_password: str, operator: str) -> bool:
        """
        修改管理员密码
        
        Args:
            admin_id (int): 管理员ID
            new_password (str): 新密码
            operator (str): 操作者用户名
            
        Returns:
            bool: 修改成功返回True，失败返回False
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取管理员信息
            cursor.execute('SELECT username FROM admins WHERE id = ?', (admin_id,))
            admin_info = cursor.fetchone()
            
            if not admin_info:
                emotion_logger.log_error(f"管理员不存在: ID {admin_id}", "修改密码", operator)
                conn.close()
                return False
            
            password_hash = self._hash_password(new_password)
            
            cursor.execute(
                'UPDATE admins SET password_hash = ? WHERE id = ?',
                (password_hash, admin_id)
            )
            
            conn.commit()
            conn.close()
            
            emotion_logger.log_user_activity(
                username=operator,
                action="修改管理员密码",
                details={"target_admin": admin_info[0]}
            )
            
            return True
            
        except Exception as e:
            emotion_logger.log_error(e, "修改管理员密码失败", operator)
            return False
    
    def is_super_admin(self, username: str) -> bool:
        """
        检查用户是否为超级管理员
        
        Args:
            username (str): 用户名
            
        Returns:
            bool: 是超级管理员返回True，否则返回False
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT role FROM admins WHERE username = ? AND is_active = 1',
                (username,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result and result[0] == self.ROLE_SUPER_ADMIN
            
        except Exception as e:
            emotion_logger.log_error(e, "检查超级管理员权限失败", username)
            return False