#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本
用于测试管理员API功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.admin_service import AdminService

def test_admin_service():
    """
    测试AdminService的各个方法
    """
    print("=== 测试AdminService ===\n")
    
    try:
        # 测试系统概览
        print("1. 测试系统概览数据...")
        overview_data = AdminService.get_system_overview()
        print("系统概览数据:")
        for key, value in overview_data.items():
            print(f"  {key}: {value}")
        print()
        
        # 测试用户统计
        print("2. 测试用户统计数据...")
        users_data = AdminService.get_users_statistics()
        print(f"用户数量: {len(users_data)}")
        if users_data:
            print("前3个用户:")
            for user in users_data[:3]:
                print(f"  {user}")
        print()
        
        # 测试说话人统计
        print("3. 测试说话人统计数据...")
        speakers_data = AdminService.get_speakers_statistics()
        print(f"说话人数量: {len(speakers_data)}")
        if speakers_data:
            print("前3个说话人:")
            for speaker in speakers_data[:3]:
                print(f"  {speaker}")
        print()
        
    except Exception as e:
        print(f"测试出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_admin_service()