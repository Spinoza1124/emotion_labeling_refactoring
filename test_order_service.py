#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试OrderService功能
验证数据库排序服务是否正常工作
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.order_service import OrderService
from services.audio_service import AudioService

def test_speaker_order():
    """
    测试说话人排序功能
    """
    print("=== 测试说话人排序功能 ===")
    
    # 模拟说话人分组
    speaker_groups = {
        'spk161': ['spk161-1', 'spk161-2', 'spk161-3'],
        'spk182': ['spk182-1', 'spk182-2'],
        'spk36': ['spk36-1', 'spk36-2'],
        'spk75': ['spk75-1', 'spk75-2']
    }
    
    username = "zhangsan"
    
    # 获取用户排序
    sorted_speakers = OrderService.get_user_speaker_order(username, speaker_groups)
    print(f"用户 {username} 的说话人排序: {sorted_speakers}")
    
    # 再次获取，应该保持一致
    sorted_speakers2 = OrderService.get_user_speaker_order(username, speaker_groups)
    print(f"再次获取的排序: {sorted_speakers2}")
    
    if sorted_speakers == sorted_speakers2:
        print("✓ 说话人排序一致性测试通过")
    else:
        print("✗ 说话人排序一致性测试失败")
    
    return sorted_speakers

def test_audio_order():
    """
    测试音频文件排序功能
    """
    print("\n=== 测试音频文件排序功能 ===")
    
    # 模拟音频文件列表
    audio_files = [
        "/path/to/spk161-1-1-124.wav",
        "/path/to/spk161-2-1-314.wav",
        "/path/to/spk161-3-1-65.wav",
        "/path/to/spk161-2-1-540.wav",
        "/path/to/spk161-2-1-487.wav"
    ]
    
    username = "zhangsan"
    speaker = "spk161"
    
    # 获取用户音频排序
    sorted_audio = OrderService.get_user_audio_order(speaker, username, audio_files)
    print(f"用户 {username} 的 {speaker} 音频排序:")
    for i, audio in enumerate(sorted_audio[:5]):
        print(f"  {i+1}. {os.path.basename(audio)}")
    
    # 再次获取，应该保持一致
    sorted_audio2 = OrderService.get_user_audio_order(speaker, username, audio_files)
    
    if sorted_audio == sorted_audio2:
        print("✓ 音频文件排序一致性测试通过")
    else:
        print("✗ 音频文件排序一致性测试失败")
    
    return sorted_audio

def test_audio_service_integration():
    """
    测试AudioService集成
    """
    print("\n=== 测试AudioService集成 ===")
    
    try:
        # 测试获取说话人列表
        speakers = AudioService.get_speakers_list("zhangsan")
        print(f"获取到的说话人列表: {speakers[:5]}...")
        
        if speakers:
            # 测试获取音频文件列表
            first_speaker = speakers[0]
            audio_files = AudioService.get_audio_files_list(first_speaker, "zhangsan")
            print(f"说话人 {first_speaker} 的音频文件数量: {len(audio_files)}")
            
            if audio_files:
                print(f"前3个音频文件:")
                for i, audio in enumerate(audio_files[:3]):
                    print(f"  {i+1}. {os.path.basename(audio)}")
                print("✓ AudioService集成测试通过")
            else:
                print("⚠ 未找到音频文件")
        else:
            print("⚠ 未找到说话人")
            
    except Exception as e:
        print(f"✗ AudioService集成测试失败: {e}")

def test_order_statistics():
    """
    测试排序统计功能
    """
    print("\n=== 测试排序统计功能 ===")
    
    username = "zhangsan"
    stats = OrderService.get_user_order_statistics(username)
    
    print(f"用户 {username} 的排序统计:")
    print(f"  说话人排序数量: {stats['speaker_orders']}")
    print(f"  音频排序数量: {stats['audio_orders']}")
    
    if stats['speaker_orders'] > 0 and stats['audio_orders'] > 0:
        print("✓ 排序统计测试通过")
    else:
        print("⚠ 排序统计数据为空")

def main():
    """
    主测试函数
    """
    print("开始测试OrderService功能...\n")
    
    try:
        # 测试说话人排序
        test_speaker_order()
        
        # 测试音频文件排序
        test_audio_order()
        
        # 测试AudioService集成
        test_audio_service_integration()
        
        # 测试排序统计
        test_order_statistics()
        
        print("\n=== 测试完成 ===")
        print("OrderService功能测试完成！")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()