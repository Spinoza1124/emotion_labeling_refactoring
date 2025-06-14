#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API端点测试脚本
用于测试管理员API端点
"""

import requests
import json

def test_admin_api():
    """
    测试管理员API端点
    """
    base_url = "http://10.10.1.213:5000"
    
    # 创建session来保持cookies
    session = requests.Session()
    
    print("=== 测试管理员API端点 ===\n")
    
    try:
        # 1. 测试登录
        print("1. 测试管理员登录...")
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = session.post(
            f"{base_url}/admin/login",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"登录响应状态码: {response.status_code}")
        print(f"登录响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✓ 登录成功")
        else:
            print("✗ 登录失败")
            return
        
        print()
        
        # 2. 测试系统概览API
        print("2. 测试系统概览API...")
        response = session.get(f"{base_url}/admin/api/overview")
        
        print(f"概览API响应状态码: {response.status_code}")
        print(f"概览API响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ 系统概览API正常")
            print("概览数据:")
            for key, value in data.items():
                print(f"  {key}: {value}")
        else:
            print("✗ 系统概览API失败")
        
        print()
        
        # 3. 测试用户API
        print("3. 测试用户API...")
        response = session.get(f"{base_url}/admin/api/users")
        
        print(f"用户API响应状态码: {response.status_code}")
        print(f"用户API响应长度: {len(response.text)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 用户API正常，返回 {len(data)} 个用户")
        else:
            print("✗ 用户API失败")
            print(f"错误内容: {response.text}")
        
        print()
        
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器")
    except Exception as e:
        print(f"✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_admin_api()