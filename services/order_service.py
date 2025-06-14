#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排序服务
处理用户的说话人和音频文件排序逻辑
"""

import os
import json
import random
from datetime import datetime
from services.database_service import DatabaseService

class OrderService:
    """排序服务类"""
    
    @staticmethod
    def get_user_speaker_order(username, speaker_groups):
        """
        获取用户专属的说话人排序
        
        Args:
            username (str): 用户名
            speaker_groups (dict): 说话人分组字典
            
        Returns:
            list: 排序后的说话人列表
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 查询用户的说话人排序
            cursor.execute(
                "SELECT speaker_order FROM user_speaker_orders WHERE username = ?",
                (username,)
            )
            result = cursor.fetchone()
            
            if result:
                # 使用保存的排序
                saved_order = json.loads(result[0])
                sorted_groups = []
                existing_groups = set(speaker_groups.keys())
                
                # 按保存的顺序重新排列
                for group in saved_order:
                    if group in existing_groups:
                        sorted_groups.append(group)
                        existing_groups.remove(group)
                
                # 添加新的说话人组
                sorted_groups.extend(list(existing_groups))
                
                # 如果有新的说话人组，更新数据库
                if existing_groups:
                    OrderService._save_user_speaker_order(username, sorted_groups)
            else:
                # 创建新的个性化排序
                speaker_group_list = list(speaker_groups.keys())
                random.seed(hash(username) % (2**32))
                random.shuffle(speaker_group_list)
                sorted_groups = speaker_group_list
                random.seed()
                
                # 保存到数据库
                OrderService._save_user_speaker_order(username, sorted_groups)
            
            conn.close()
            return sorted_groups
            
        except Exception as e:
            print(f"获取用户说话人排序失败: {e}")
            # 降级处理：返回随机排序
            speaker_group_list = list(speaker_groups.keys())
            random.seed(hash(username) % (2**32))
            random.shuffle(speaker_group_list)
            random.seed()
            return speaker_group_list
    
    @staticmethod
    def _save_user_speaker_order(username, speaker_order):
        """
        保存用户的说话人排序到数据库
        
        Args:
            username (str): 用户名
            speaker_order (list): 说话人排序列表
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_speaker_orders 
                (username, speaker_order, updated_at)
                VALUES (?, ?, ?)
            ''', (
                username,
                json.dumps(speaker_order, ensure_ascii=False),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"保存用户说话人排序失败: {e}")
    
    @staticmethod
    def get_user_audio_order(speaker, username, audio_files):
        """
        获取用户专属的音频文件排序
        
        Args:
            speaker (str): 说话人
            username (str): 用户名
            audio_files (list): 音频文件列表
            
        Returns:
            list: 排序后的音频文件列表
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 查询用户的音频文件排序
            cursor.execute(
                "SELECT audio_order FROM user_audio_orders WHERE username = ? AND speaker = ?",
                (username, speaker)
            )
            result = cursor.fetchone()
            
            audio_file_names = [os.path.basename(f) for f in audio_files]
            
            if result:
                # 使用保存的排序
                saved_order = json.loads(result[0])
                sorted_files = []
                saved_names = set(saved_order)
                current_names = set(audio_file_names)
                
                # 添加已保存顺序的文件
                for name in saved_order:
                    if name in current_names:
                        for full_path in audio_files:
                            if os.path.basename(full_path) == name:
                                sorted_files.append(full_path)
                                break
                
                # 添加新文件
                new_files = current_names - saved_names
                if new_files:
                    new_file_paths = [f for f in audio_files if os.path.basename(f) in new_files]
                    seed_string = f"{username}_{speaker}_new"
                    random.seed(hash(seed_string) % (2**32))
                    random.shuffle(new_file_paths)
                    random.seed()
                    sorted_files.extend(new_file_paths)
                    
                    # 更新保存的顺序
                    updated_order = [os.path.basename(f) for f in sorted_files]
                    OrderService._save_user_audio_order(username, speaker, updated_order)
            else:
                # 创建新的排序
                seed_string = f"{username}_{speaker}"
                random.seed(hash(seed_string) % (2**32))
                random.shuffle(audio_files)
                random.seed()
                sorted_files = audio_files
                
                # 保存排序
                audio_order = [os.path.basename(f) for f in sorted_files]
                OrderService._save_user_audio_order(username, speaker, audio_order)
            
            conn.close()
            return sorted_files
            
        except Exception as e:
            print(f"获取用户音频排序失败: {e}")
            # 降级处理：返回随机排序
            seed_string = f"{username}_{speaker}"
            random.seed(hash(seed_string) % (2**32))
            random.shuffle(audio_files)
            random.seed()
            return audio_files
    
    @staticmethod
    def _save_user_audio_order(username, speaker, audio_order):
        """
        保存用户的音频文件排序到数据库
        
        Args:
            username (str): 用户名
            speaker (str): 说话人
            audio_order (list): 音频文件排序列表
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_audio_orders 
                (username, speaker, audio_order, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (
                username,
                speaker,
                json.dumps(audio_order, ensure_ascii=False),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"保存用户音频排序失败: {e}")
    
    @staticmethod
    def delete_user_orders(username):
        """
        删除用户的所有排序数据
        
        Args:
            username (str): 用户名
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 删除说话人排序
            cursor.execute(
                "DELETE FROM user_speaker_orders WHERE username = ?",
                (username,)
            )
            
            # 删除音频排序
            cursor.execute(
                "DELETE FROM user_audio_orders WHERE username = ?",
                (username,)
            )
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"删除用户排序数据失败: {e}")
    
    @staticmethod
    def get_user_order_statistics(username):
        """
        获取用户排序统计信息
        
        Args:
            username (str): 用户名
            
        Returns:
            dict: 统计信息
        """
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            
            # 获取说话人排序数量
            cursor.execute(
                "SELECT COUNT(*) FROM user_speaker_orders WHERE username = ?",
                (username,)
            )
            speaker_orders = cursor.fetchone()[0]
            
            # 获取音频排序数量
            cursor.execute(
                "SELECT COUNT(*) FROM user_audio_orders WHERE username = ?",
                (username,)
            )
            audio_orders = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'speaker_orders': speaker_orders,
                'audio_orders': audio_orders
            }
            
        except Exception as e:
            print(f"获取用户排序统计失败: {e}")
            return {
                'speaker_orders': 0,
                'audio_orders': 0
            }