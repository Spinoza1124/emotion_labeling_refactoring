/**
 * 登录页面JavaScript逻辑
 */

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initLoginForm();
});

/**
 * 初始化登录表单
 */
function initLoginForm() {
    const form = document.querySelector('form');
    const submitBtn = document.querySelector('.btn');
    
    if (form) {
        form.addEventListener('submit', handleLogin);
    }
}

/**
 * 处理登录表单提交
 * @param {Event} event - 表单提交事件
 */
function handleLogin(event) {
    event.preventDefault();
    
    const wechatName = document.getElementById('text1').value.trim();
    const phoneNumber = document.getElementById('myInput').value.trim();
    const submitBtn = document.querySelector('.btn');
    
    // 验证输入
    if (!wechatName) {
        showError('请输入微信昵称');
        return;
    }
    
    if (!phoneNumber) {
        showError('请输入手机号');
        return;
    }
    
    // 验证手机号格式
    if (!isValidPhoneNumber(phoneNumber)) {
        showError('请输入正确的手机号格式');
        return;
    }
    
    // 禁用提交按钮，防止重复提交
    submitBtn.disabled = true;
    submitBtn.textContent = '登录中...';
    
    // 发送登录请求
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text1: wechatName,
            password: phoneNumber
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 登录成功，显示成功消息
            showSuccess(data.message);
            
            // 添加调试信息
            console.log('登录响应数据:', data);
            console.log('skip_test:', data.skip_test, '类型:', typeof data.skip_test);
            console.log('skip_consistency_test:', data.skip_consistency_test, '类型:', typeof data.skip_consistency_test);
            
            // 根据测试跳过设置决定跳转页面
            setTimeout(() => {
                if (!data.skip_test) {
                    console.log('重定向到测试页面');
                    // 需要进行测试
                    window.location.href = '/test';
                } else if (!data.skip_consistency_test) {
                    console.log('重定向到一致性测试页面');
                    // 跳过测试但需要进行一致性检验
                    window.location.href = '/consistency_test';
                } else {
                    console.log('重定向到主页面');
                    // 跳过所有测试，直接进入主页面
                    window.location.href = '/main';
                }
            }, 1000);
        } else {
            showError(data.message || '登录失败，请重试');
        }
    })
    .catch(error => {
        console.error('登录请求失败:', error);
        showError('网络错误，请检查网络连接后重试');
    })
    .finally(() => {
        // 恢复提交按钮状态
        submitBtn.disabled = false;
        submitBtn.textContent = '登录';
    });
}

/**
 * 验证手机号格式
 * @param {string} phoneNumber - 手机号
 * @returns {boolean} 是否为有效手机号
 */
function isValidPhoneNumber(phoneNumber) {
    // 简单的手机号验证：11位数字，以1开头
    const phoneRegex = /^1[3-9]\d{9}$/;
    return phoneRegex.test(phoneNumber);
}

/**
 * 显示错误信息
 * @param {string} message - 错误信息
 */
function showError(message) {
    removeExistingMessages();
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = `
        color: #ff4444;
        background-color: #ffe6e6;
        border: 1px solid #ff4444;
        padding: 10px;
        margin: 10px 0;
        border-radius: 4px;
        text-align: center;
        font-size: 14px;
    `;
    errorDiv.textContent = message;
    
    const form = document.querySelector('form');
    form.insertBefore(errorDiv, form.firstChild);
    
    // 3秒后自动移除错误信息
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 3000);
}

/**
 * 显示成功信息
 * @param {string} message - 成功信息
 */
function showSuccess(message) {
    removeExistingMessages();
    
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.style.cssText = `
        color: #00aa00;
        background-color: #e6ffe6;
        border: 1px solid #00aa00;
        padding: 10px;
        margin: 10px 0;
        border-radius: 4px;
        text-align: center;
        font-size: 14px;
    `;
    successDiv.textContent = message;
    
    const form = document.querySelector('form');
    form.insertBefore(successDiv, form.firstChild);
}

/**
 * 移除现有的消息提示
 */
function removeExistingMessages() {
    const existingMessages = document.querySelectorAll('.error-message, .success-message');
    existingMessages.forEach(msg => {
        if (msg.parentNode) {
            msg.parentNode.removeChild(msg);
        }
    });
}

