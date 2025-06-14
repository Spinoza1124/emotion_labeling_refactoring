/**
 * 用户管理模块
 * 负责用户登录、认证和用户信息管理
 */
class UserManager {
    constructor() {
        this.currentUsername = '';
        this.previousUsername = '';
    }

    /**
     * 初始化用户认证
     */
    async initAuth() {
        try {
            // 通过服务器端验证用户会话状态
            const response = await fetch('/api/user/session-status', {
                method: 'GET',
                credentials: 'same-origin'  // 确保发送Cookie
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.authenticated) {
                    this.previousUsername = this.currentUsername;
                    this.currentUsername = data.username;
                    return true;
                } else {
                    // 用户未登录，重定向到登录页面
                    window.location.href = '/login';
                    return false;
                }
            } else {
                // 请求失败，重定向到登录页面
                window.location.href = '/login';
                return false;
            }
        } catch (error) {
            console.error('验证用户会话时出错:', error);
            window.location.href = '/login';
            return false;
        }
    }

    /**
     * 检查用户测试设置并重定向
     */
    async checkUserTestSettings(username) {
        try {
            const response = await fetch('/api/user/test-settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username: username })
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log('用户测试设置:', data);
                
                // 根据测试设置决定重定向页面
                if (!data.skip_test) {
                    console.log('重定向到测试页面');
                    window.location.href = '/test?username=' + encodeURIComponent(username);
                } else if (!data.skip_consistency_test) {
                    console.log('重定向到一致性测试页面');
                    window.location.href = '/consistency_test?username=' + encodeURIComponent(username);
                } else {
                    console.log('重定向到主页面');
                    window.location.href = '/main?username=' + encodeURIComponent(username) + '&keep_login=true';
                }
            } else {
                // 如果获取设置失败，默认跳转到测试页面
                console.log('获取用户设置失败，跳转到测试页面');
                window.location.href = '/test?username=' + encodeURIComponent(username);
            }
        } catch (error) {
            console.error('检查用户测试设置时出错:', error);
            // 出错时默认跳转到测试页面
            window.location.href = '/test?username=' + encodeURIComponent(username);
        }
    }

    /**
     * 退出登录
     */
    logout() {
        if(confirm('确定要退出登录吗？')) {
            // 直接重定向到服务器端的退出登录路由
            // 服务器会清除会话和Cookie
            window.location.href = '/logout';
        }
    }

    /**
     * 更新用户名
     */
    updateUsername(oldUsername, newUsername) {
        if (!oldUsername || !newUsername) return;
        
        return fetch('/api/update_username', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                old_username: oldUsername,
                new_username: newUsername
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log(`已移动 ${data.moved_files} 个文件到新用户目录`);
                return data;
            } else {
                throw new Error(data.error);
            }
        });
    }

    getCurrentUsername() {
        return this.currentUsername;
    }

    setCurrentUsername(username) {
        this.currentUsername = username;
    }
}

