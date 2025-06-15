#!/usr/bin/env python3
import sqlite3

def check_user_status():
    try:
        # 检查用户数据库
        conn = sqlite3.connect('/mnt/shareEEx/liuyang/code/emotion_labeling_refactoring/database/users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT wechat_name, skip_consistency_test FROM users WHERE wechat_name = ?', ('zhangsan',))
        result = cursor.fetchone()
        
        if result:
            print(f'用户 {result[0]} 的skip_consistency_test状态: {result[1]}')
            
            # 如果状态为1，重置为0（需要进行一致性测试）
            if result[1] == 1:
                cursor.execute('UPDATE users SET skip_consistency_test = 0 WHERE wechat_name = ?', ('zhangsan',))
                conn.commit()
                print('已将zhangsan的skip_consistency_test状态重置为0（需要进行一致性测试）')
        else:
            print('未找到用户zhangsan')
        
        conn.close()
        
        # 检查一致性测试结果数据库 - 应该在emotion_labels.db中
        try:
            conn2 = sqlite3.connect('/mnt/shareEEx/liuyang/code/emotion_labeling_refactoring/database/emotion_labels.db')
            cursor2 = conn2.cursor()
            
            cursor2.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='consistency_test_results'")
            table_exists = cursor2.fetchone()
            
            if table_exists:
                cursor2.execute('SELECT COUNT(*) FROM consistency_test_results WHERE username = ?', ('zhangsan',))
                count = cursor2.fetchone()[0]
                print(f'zhangsan在emotion_labels.db中的一致性测试结果数量: {count}')
                
                # 显示前几条记录
                cursor2.execute('SELECT audio_file, v_value, a_value, discrete_emotion FROM consistency_test_results WHERE username = ? LIMIT 5', ('zhangsan',))
                records = cursor2.fetchall()
                print('前5条记录:')
                for record in records:
                    print(f'  音频: {record[0]}, V值: {record[1]}, A值: {record[2]}, 情绪: {record[3]}')
            else:
                print('在emotion_labels.db中未找到consistency_test_results表')
            
            conn2.close()
        except Exception as e:
            print(f'检查emotion_labels.db时出错: {e}')
            
    except Exception as e:
        print(f'检查用户状态时出错: {e}')

if __name__ == '__main__':
    check_user_status()