/**
 * 管理员仪表板JavaScript
 * 处理管理员后台的前端交互逻辑
 */

class AdminDashboard {
    /**
     * 初始化管理员仪表板
     */
    constructor() {
        this.currentSection = 'overview';
        this.charts = {};
        this.init();
    }

    /**
     * 初始化仪表板
     */
    init() {
        this.bindEvents();
        this.loadOverviewData();
        this.setupNavigation();
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 登出按钮
        document.getElementById('logout-btn').addEventListener('click', () => {
            this.logout();
        });

        // 刷新按钮
        document.getElementById('refresh-users')?.addEventListener('click', () => {
            this.loadUsersData();
        });

        document.getElementById('refresh-speakers')?.addEventListener('click', () => {
            this.loadSpeakersData();
        });

        document.getElementById('refresh-system-status')?.addEventListener('click', () => {
            this.loadSystemStatus();
        });

        // 导出按钮
        document.getElementById('export-btn')?.addEventListener('click', () => {
            this.exportData();
        });

        document.getElementById('backup-btn')?.addEventListener('click', () => {
            this.backupDatabase();
        });

        // 模态框关闭
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => {
                e.target.closest('.modal').style.display = 'none';
            });
        });

        // 点击模态框外部关闭
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.style.display = 'none';
            }
        });
    }

    /**
     * 设置导航
     */
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.dataset.section;
                this.switchSection(section);
            });
        });
    }

    /**
     * 切换页面部分
     * @param {string} section - 要切换到的部分
     */
    switchSection(section) {
        // 更新导航状态
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // 更新内容区域
        document.querySelectorAll('.content-section').forEach(sec => {
            sec.classList.remove('active');
        });
        document.getElementById(`${section}-section`).classList.add('active');

        this.currentSection = section;

        // 加载对应数据
        this.loadSectionData(section);
    }

    /**
     * 加载指定部分的数据
     * @param {string} section - 部分名称
     */
    loadSectionData(section) {
        switch (section) {
            case 'overview':
                this.loadOverviewData();
                break;
            case 'users':
                this.loadUsersData();
                break;
            case 'speakers':
                this.loadSpeakersData();
                break;
            case 'progress':
                this.loadProgressData();
                break;
            case 'quality':
                this.loadQualityData();
                break;
            case 'system':
                this.loadSystemStatus();
                break;
        }
    }

    /**
     * 加载系统概览数据
     */
    async loadOverviewData() {
        try {
            const response = await fetch('/admin/api/overview');
            const data = await response.json();

            if (response.ok) {
                this.updateOverviewUI(data);
            } else {
                this.showError('加载概览数据失败: ' + data.error);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    /**
     * 更新概览界面
     * @param {Object} data - 概览数据
     */
    updateOverviewUI(data) {
        document.getElementById('total-users').textContent = data.total_users;
        document.getElementById('total-audio-files').textContent = data.total_audio_files;
        document.getElementById('total-annotations').textContent = data.total_annotations;
        document.getElementById('completion-rate').textContent = data.completion_rate + '%';
        document.getElementById('today-annotations').textContent = data.today_annotations;
        document.getElementById('active-users').textContent = data.active_users;
    }

    /**
     * 加载用户数据
     */
    async loadUsersData() {
        try {
            const response = await fetch('/admin/api/users');
            const data = await response.json();

            if (response.ok) {
                this.updateUsersTable(data);
            } else {
                this.showError('加载用户数据失败: ' + data.error);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    /**
     * 更新用户表格
     * @param {Array} users - 用户数据数组
     */
    updateUsersTable(users) {
        const tbody = document.querySelector('#users-table tbody');
        tbody.innerHTML = '';

        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.username}</td>
                <td>${user.total_annotations}</td>
                <td>${user.completed_annotations}</td>
                <td>${user.completion_rate}%</td>
                <td>${user.speakers_count}</td>
                <td>${user.avg_play_count}</td>
                <td>${user.last_annotation || '-'}</td>
                <td>
                    <button class="btn btn-primary action-btn" onclick="adminDashboard.showUserDetails('${user.username}')">详情</button>
                    <button class="btn btn-danger action-btn" onclick="adminDashboard.confirmResetUser('${user.username}')">重置</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    /**
     * 显示用户详情
     * @param {string} username - 用户名
     */
    async showUserDetails(username) {
        try {
            const response = await fetch(`/admin/api/users/${username}/details`);
            const data = await response.json();

            if (response.ok) {
                this.displayUserDetails(data);
            } else {
                this.showError('加载用户详情失败: ' + data.error);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    /**
     * 显示用户详情模态框
     * @param {Object} userDetails - 用户详情数据
     */
    displayUserDetails(userDetails) {
        document.getElementById('modal-username').textContent = `用户详情 - ${userDetails.username}`;
        
        const content = document.getElementById('user-detail-content');
        content.innerHTML = `
            <div class="user-summary">
                <h4>基本信息</h4>
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="status-label">总标注数:</span>
                        <span class="status-value">${userDetails.total_annotations}</span>
                    </div>
                    <div class="stat-item">
                        <span class="status-label">完成数:</span>
                        <span class="status-value">${userDetails.completed_annotations}</span>
                    </div>
                    <div class="stat-item">
                        <span class="status-label">完成率:</span>
                        <span class="status-value">${userDetails.completion_rate}%</span>
                    </div>
                    <div class="stat-item">
                        <span class="status-label">说话人数:</span>
                        <span class="status-value">${userDetails.speakers_count}</span>
                    </div>
                    <div class="stat-item">
                        <span class="status-label">总时长:</span>
                        <span class="status-value">${userDetails.total_duration}秒</span>
                    </div>
                    <div class="stat-item">
                        <span class="status-label">平均播放次数:</span>
                        <span class="status-value">${userDetails.avg_play_count}</span>
                    </div>
                </div>
            </div>
            
            <div class="speakers-stats">
                <h4>按说话人统计</h4>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>说话人</th>
                            <th>标注数</th>
                            <th>完成数</th>
                            <th>完成率</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${userDetails.speakers_stats.map(speaker => `
                            <tr>
                                <td>${speaker.speaker}</td>
                                <td>${speaker.annotations_count}</td>
                                <td>${speaker.completed_count}</td>
                                <td>${speaker.completion_rate}%</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            
            <div class="recent-annotations">
                <h4>最近标注</h4>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>音频文件</th>
                            <th>说话人</th>
                            <th>VA完成</th>
                            <th>离散完成</th>
                            <th>时间</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${userDetails.recent_annotations.map(annotation => `
                            <tr>
                                <td>${annotation.audio_file}</td>
                                <td>${annotation.speaker}</td>
                                <td>${annotation.va_complete ? '✅' : '❌'}</td>
                                <td>${annotation.discrete_complete ? '✅' : '❌'}</td>
                                <td>${annotation.timestamp}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        document.getElementById('user-detail-modal').style.display = 'block';
    }

    /**
     * 加载说话人数据
     */
    async loadSpeakersData() {
        try {
            const response = await fetch('/admin/api/speakers');
            const data = await response.json();

            if (response.ok) {
                this.updateSpeakersTable(data);
            } else {
                this.showError('加载说话人数据失败: ' + data.error);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    /**
     * 更新说话人表格
     * @param {Array} speakers - 说话人数据数组
     */
    updateSpeakersTable(speakers) {
        const tbody = document.querySelector('#speakers-table tbody');
        tbody.innerHTML = '';

        speakers.forEach(speaker => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${speaker.speaker}</td>
                <td>${speaker.total_annotations}</td>
                <td>${speaker.completed_annotations}</td>
                <td>${speaker.completion_rate}%</td>
                <td>${speaker.annotators_count}</td>
                <td>${speaker.audio_files_count}</td>
                <td>${speaker.total_duration}</td>
            `;
            tbody.appendChild(row);
        });
    }

    /**
     * 加载进度数据
     */
    async loadProgressData() {
        try {
            const response = await fetch('/admin/api/progress');
            const data = await response.json();

            if (response.ok) {
                this.updateProgressCharts(data);
            } else {
                this.showError('加载进度数据失败: ' + data.error);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    /**
     * 更新进度图表
     * @param {Object} data - 进度数据
     */
    updateProgressCharts(data) {
        // 每日进度图表
        const dailyCtx = document.getElementById('daily-progress-chart').getContext('2d');
        if (this.charts.dailyProgress) {
            this.charts.dailyProgress.destroy();
        }
        
        this.charts.dailyProgress = new Chart(dailyCtx, {
            type: 'line',
            data: {
                labels: data.daily_progress.map(d => d.date),
                datasets: [{
                    label: '每日标注数',
                    data: data.daily_progress.map(d => d.annotations),
                    borderColor: 'rgb(102, 126, 234)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.1
                }, {
                    label: '每日完成数',
                    data: data.daily_progress.map(d => d.completed),
                    borderColor: 'rgb(118, 75, 162)',
                    backgroundColor: 'rgba(118, 75, 162, 0.1)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // 本周用户活跃度图表
        const weeklyCtx = document.getElementById('weekly-users-chart').getContext('2d');
        if (this.charts.weeklyUsers) {
            this.charts.weeklyUsers.destroy();
        }
        
        this.charts.weeklyUsers = new Chart(weeklyCtx, {
            type: 'bar',
            data: {
                labels: data.weekly_user_progress.map(u => u.username),
                datasets: [{
                    label: '本周标注数',
                    data: data.weekly_user_progress.map(u => u.annotations),
                    backgroundColor: 'rgba(102, 126, 234, 0.8)'
                }, {
                    label: '本周完成数',
                    data: data.weekly_user_progress.map(u => u.completed),
                    backgroundColor: 'rgba(118, 75, 162, 0.8)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    /**
     * 加载质量数据
     */
    async loadQualityData() {
        try {
            const response = await fetch('/admin/api/quality');
            const data = await response.json();

            if (response.ok) {
                this.updateQualityCharts(data);
            } else {
                this.showError('加载质量数据失败: ' + data.error);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    /**
     * 更新质量图表
     * @param {Object} data - 质量数据
     */
    updateQualityCharts(data) {
        // 播放次数分布
        const playCountCtx = document.getElementById('play-count-chart').getContext('2d');
        if (this.charts.playCount) {
            this.charts.playCount.destroy();
        }
        
        this.charts.playCount = new Chart(playCountCtx, {
            type: 'doughnut',
            data: {
                labels: data.play_count_distribution.map(d => d.range),
                datasets: [{
                    data: data.play_count_distribution.map(d => d.count),
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF'
                    ]
                }]
            },
            options: {
                responsive: true
            }
        });

        // 情感类型分布
        const emotionTypeCtx = document.getElementById('emotion-type-chart').getContext('2d');
        if (this.charts.emotionType) {
            this.charts.emotionType.destroy();
        }
        
        this.charts.emotionType = new Chart(emotionTypeCtx, {
            type: 'pie',
            data: {
                labels: data.emotion_type_distribution.map(d => d.type),
                datasets: [{
                    data: data.emotion_type_distribution.map(d => d.count),
                    backgroundColor: ['#667eea', '#764ba2']
                }]
            },
            options: {
                responsive: true
            }
        });

        // 离散情感分布
        const discreteEmotionCtx = document.getElementById('discrete-emotion-chart').getContext('2d');
        if (this.charts.discreteEmotion) {
            this.charts.discreteEmotion.destroy();
        }
        
        this.charts.discreteEmotion = new Chart(discreteEmotionCtx, {
            type: 'bar',
            data: {
                labels: data.discrete_emotion_distribution.map(d => d.emotion),
                datasets: [{
                    label: '数量',
                    data: data.discrete_emotion_distribution.map(d => d.count),
                    backgroundColor: 'rgba(102, 126, 234, 0.8)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    /**
     * 导出数据
     */
    async exportData() {
        const format = document.getElementById('export-format').value;
        const username = document.getElementById('export-username').value;
        const speaker = document.getElementById('export-speaker').value;

        const params = new URLSearchParams({ format });
        if (username) params.append('username', username);
        if (speaker) params.append('speaker', speaker);

        try {
            const response = await fetch(`/admin/api/export?${params}`);
            const data = await response.json();

            if (response.ok) {
                this.showSuccess(`导出成功！文件: ${data.filename}，记录数: ${data.record_count}`);
            } else {
                this.showError('导出失败: ' + data.error);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    /**
     * 备份数据库
     */
    async backupDatabase() {
        try {
            const response = await fetch('/admin/api/backup', { method: 'POST' });
            const data = await response.json();

            if (response.ok) {
                this.showSuccess(`备份成功！文件: ${data.backup_filename}`);
            } else {
                this.showError('备份失败: ' + data.error);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    /**
     * 确认重置用户
     * @param {string} username - 用户名
     */
    confirmResetUser(username) {
        document.getElementById('confirm-message').textContent = `确定要重置用户 "${username}" 的所有标注数据吗？此操作不可恢复！`;
        
        document.getElementById('confirm-yes').onclick = () => {
            this.resetUser(username);
            document.getElementById('confirm-modal').style.display = 'none';
        };
        
        document.getElementById('confirm-no').onclick = () => {
            document.getElementById('confirm-modal').style.display = 'none';
        };
        
        document.getElementById('confirm-modal').style.display = 'block';
    }

    /**
     * 重置用户数据
     * @param {string} username - 用户名
     */
    async resetUser(username) {
        try {
            const response = await fetch(`/admin/api/users/${username}/reset`, { method: 'POST' });
            const data = await response.json();

            if (response.ok) {
                this.showSuccess(`重置成功！删除了 ${data.deleted_records} 条记录`);
                this.loadUsersData(); // 刷新用户列表
            } else {
                this.showError('重置失败: ' + data.error);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    /**
     * 加载系统状态
     */
    async loadSystemStatus() {
        try {
            const response = await fetch('/admin/api/system/status');
            const data = await response.json();

            if (response.ok) {
                this.updateSystemStatus(data);
            } else {
                this.showError('加载系统状态失败: ' + data.error);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    /**
     * 更新系统状态显示
     * @param {Object} data - 系统状态数据
     */
    updateSystemStatus(data) {
        // 数据库状态
        const dbStatus = document.getElementById('database-status');
        dbStatus.innerHTML = `
            <div class="status-item">
                <span class="status-label">数据库存在:</span>
                <span class="status-value ${data.database.exists ? 'status-good' : 'status-error'}">
                    ${data.database.exists ? '✅ 是' : '❌ 否'}
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">数据库可访问:</span>
                <span class="status-value ${data.database.accessible ? 'status-good' : 'status-error'}">
                    ${data.database.accessible ? '✅ 是' : '❌ 否'}
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">数据库大小:</span>
                <span class="status-value">${data.database.size_mb} MB</span>
            </div>
            <div class="status-item">
                <span class="status-label">总记录数:</span>
                <span class="status-value">${data.database.total_records}</span>
            </div>
        `;

        // 音频文件夹状态
        const audioStatus = document.getElementById('audio-folder-status');
        audioStatus.innerHTML = `
            <div class="status-item">
                <span class="status-label">文件夹存在:</span>
                <span class="status-value ${data.audio_folder.exists ? 'status-good' : 'status-error'}">
                    ${data.audio_folder.exists ? '✅ 是' : '❌ 否'}
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">路径:</span>
                <span class="status-value">${data.audio_folder.path}</span>
            </div>
        `;

        // 磁盘空间状态
        const diskStatus = document.getElementById('disk-space-status');
        const usageClass = data.disk_space.usage_percent > 90 ? 'status-error' : 
                          data.disk_space.usage_percent > 80 ? 'status-warning' : 'status-good';
        
        diskStatus.innerHTML = `
            <div class="status-item">
                <span class="status-label">总空间:</span>
                <span class="status-value">${data.disk_space.total_gb} GB</span>
            </div>
            <div class="status-item">
                <span class="status-label">已使用:</span>
                <span class="status-value">${data.disk_space.used_gb} GB</span>
            </div>
            <div class="status-item">
                <span class="status-label">可用空间:</span>
                <span class="status-value">${data.disk_space.free_gb} GB</span>
            </div>
            <div class="status-item">
                <span class="status-label">使用率:</span>
                <span class="status-value ${usageClass}">${data.disk_space.usage_percent}%</span>
            </div>
        `;
    }

    /**
     * 登出
     */
    async logout() {
        try {
            const response = await fetch('/admin/logout', { method: 'POST' });
            if (response.ok) {
                window.location.href = '/admin/login';
            }
        } catch (error) {
            this.showError('登出失败: ' + error.message);
        }
    }

    /**
     * 显示成功消息
     * @param {string} message - 消息内容
     */
    showSuccess(message) {
        const resultDiv = document.getElementById('export-result');
        resultDiv.className = 'result-message success';
        resultDiv.textContent = message;
        resultDiv.style.display = 'block';
        
        setTimeout(() => {
            resultDiv.style.display = 'none';
        }, 5000);
    }

    /**
     * 显示错误消息
     * @param {string} message - 错误消息
     */
    showError(message) {
        const resultDiv = document.getElementById('export-result');
        resultDiv.className = 'result-message error';
        resultDiv.textContent = message;
        resultDiv.style.display = 'block';
        
        setTimeout(() => {
            resultDiv.style.display = 'none';
        }, 5000);
    }
}

// 初始化管理员仪表板
let adminDashboard;
document.addEventListener('DOMContentLoaded', () => {
    adminDashboard = new AdminDashboard();
});