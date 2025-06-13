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
    initAuth() {
        const savedUsername = localStorage.getItem('emotion_labeling_username');
        
        if (savedUsername) {
            const urlParams = new URLSearchParams(window.location.search);
            const keepLogin = urlParams.get('keep_login');
            
            if (!keepLogin) {
                window.location.href = '/test?username=' + encodeURIComponent(savedUsername);
                return false;
            }
            
            this.previousUsername = this.currentUsername;
            this.currentUsername = savedUsername;
            return true;
        } else {
            window.location.href = '/login';
            return false;
        }
    }

    /**
     * 退出登录
     */
    logout() {
        if(confirm('确定要退出登录吗？')) {
            localStorage.removeItem('emotion_labeling_username');
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

