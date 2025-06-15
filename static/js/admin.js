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

        document.getElementById('refresh-admins')?.addEventListener('click', () => {
            this.loadAdminsData();
        });

        document.getElementById('refresh-test-settings')?.addEventListener('click', () => {
            this.loadTestSettingsData();
        });

        document.getElementById('refresh-speakers')?.addEventListener('click', () => {
            this.loadSpeakersData();
        });

        document.getElementById('refresh-system-status')?.addEventListener('click', () => {
            this.loadSystemStatus();
        });

        // 管理员管理按钮
        document.getElementById('create-admin-btn')?.addEventListener('click', () => {
            this.showCreateAdminModal();
        });

        document.getElementById('change-password-btn')?.addEventListener('click', () => {
            this.showChangePasswordModal();
        });

        // 管理员表单提交
        document.getElementById('create-admin-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createAdmin();
        });

        document.getElementById('change-password-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.changePassword();
        });

        // 导出按钮
        document.getElementById('export-btn')?.addEventListener('click', () => {
            this.exportData();
        });
        
        // 直接下载按钮
        document.getElementById('download-btn')?.addEventListener('click', () => {
            this.downloadData();
        });

        document.getElementById('backup-btn')?.addEventListener('click', () => {
            this.backupDatabase();
        });

        // 一致性分析按钮
        document.getElementById('calculate-consistency')?.addEventListener('click', () => {
            this.calculateConsistency();
        });

        document.getElementById('export-consistency-data')?.addEventListener('click', () => {
            this.exportConsistencyReport();
        });

        document.getElementById('generate-consistency-report')?.addEventListener('click', () => {
            this.generateDetailedConsistencyReport();
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
            case 'admins':
                this.loadAdminsData();
                break;
            case 'test-settings':
                this.loadTestSettingsData();
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
            case 'consistency':
                this.loadConsistencyData();
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
     * 直接下载数据
     */
    async downloadData() {
        const format = document.getElementById('export-format').value;
        const username = document.getElementById('export-username').value;
        const speaker = document.getElementById('export-speaker').value;

        const params = new URLSearchParams({ format });
        if (username) params.append('username', username);
        if (speaker) params.append('speaker', speaker);

        try {
            // 创建一个隐藏的链接来触发下载
            const downloadUrl = `/admin/api/export/download?${params}`;
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.showSuccess('文件下载已开始');
        } catch (error) {
            this.showError('下载失败: ' + error.message);
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
            console.log('开始执行登出操作');
            const response = await fetch('/admin/logout', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });
            
            console.log('登出响应状态:', response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log('登出响应数据:', data);
                // 清除本地存储的管理员信息
                sessionStorage.clear();
                localStorage.clear();
                // 跳转到登录页面
                window.location.href = '/admin/login';
            } else {
                const errorData = await response.json();
                console.error('登出失败:', errorData);
                this.showError('登出失败: ' + (errorData.error || errorData.message || '未知错误'));
            }
        } catch (error) {
            console.error('登出异常:', error);
            // 即使出现网络错误，也尝试清除本地数据并跳转
            sessionStorage.clear();
            localStorage.clear();
            this.showError('网络错误，正在跳转到登录页面...');
            setTimeout(() => {
                window.location.href = '/admin/login';
            }, 1000);
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

    /**
     * 加载一致性分析数据
     */
    async loadConsistencyData() {
        try {
            // 加载统计信息
            const statsResponse = await fetch('/admin/api/consistency/stats');
            const statsData = await statsResponse.json();
            
            if (statsResponse.ok) {
                this.updateConsistencyStats(statsData);
            }
            
            // 加载用户列表
            const usersResponse = await fetch('/admin/api/consistency/users');
            const usersData = await usersResponse.json();
            
            if (usersResponse.ok) {
                this.updateConsistencyUserSelect(usersData.users);
            }
        } catch (error) {
            this.showError('加载一致性数据失败: ' + error.message);
        }
    }

    /**
     * 更新一致性统计信息
     * @param {Object} data - 统计数据
     */
    updateConsistencyStats(data) {
        document.getElementById('consistency-users-count').textContent = data.users_count;
        document.getElementById('consistency-samples-count').textContent = data.samples_count;
    }

    /**
     * 更新一致性用户选择下拉框
     * @param {Array} users - 用户列表
     */
    updateConsistencyUserSelect(users) {
        const select = document.getElementById('consistency-user-select');
        select.innerHTML = '<option value="">请选择用户</option>';
        
        users.forEach(user => {
            const option = document.createElement('option');
            option.value = user;
            option.textContent = user;
            select.appendChild(option);
        });
    }

    /**
     * 计算用户一致性
     */
    async calculateConsistency() {
        const username = document.getElementById('consistency-user-select').value;
        
        if (!username) {
            this.showError('请先选择用户');
            return;
        }
        
        try {
            const response = await fetch(`/admin/api/consistency/calculate/${username}`);
            const data = await response.json();
            
            if (response.ok) {
                this.displayConsistencyReport(data);
            } else {
                this.showError('计算一致性失败: ' + data.error);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    /**
     * 显示一致性报告
     * @param {Object} data - 一致性数据
     */
    displayConsistencyReport(data) {
        const reportDiv = document.getElementById('consistency-results');
        
        reportDiv.innerHTML = `
            <h4>用户 ${data.username} 的一致性分析报告</h4>
            <div class="consistency-summary">
                <p><strong>总样本数:</strong> ${data.total_samples}</p>
                <p><strong>总体一致性:</strong> ${data.overall_consistency.toFixed(2)}%</p>
            </div>
            
            <div class="consistency-details">
                <h5>各维度一致性:</h5>
                <table class="consistency-table">
                    <thead>
                        <tr>
                            <th>维度</th>
                            <th>一致样本数</th>
                            <th>一致性百分比</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>V值 (效价)</td>
                            <td>${data.consistency_scores.v_value}</td>
                            <td>${data.consistency_percentages.v_value.toFixed(2)}%</td>
                        </tr>
                        <tr>
                            <td>A值 (唤醒度)</td>
                            <td>${data.consistency_scores.a_value}</td>
                            <td>${data.consistency_percentages.a_value.toFixed(2)}%</td>
                        </tr>
                        <tr>
                            <td>情感类型</td>
                            <td>${data.consistency_scores.emotion_type}</td>
                            <td>${data.consistency_percentages.emotion_type.toFixed(2)}%</td>
                        </tr>
                        <tr>
                            <td>离散情感</td>
                            <td>${data.consistency_scores.discrete_emotion}</td>
                            <td>${data.consistency_percentages.discrete_emotion.toFixed(2)}%</td>
                        </tr>
                        <tr>
                            <td>患者状态</td>
                            <td>${data.consistency_scores.patient_status}</td>
                            <td>${data.consistency_percentages.patient_status.toFixed(2)}%</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `;
        
        // 存储详细结果用于导出
        this.currentConsistencyData = data;
        
        reportDiv.style.display = 'block';
    }

    /**
     * 导出一致性报告
     */
    exportConsistencyReport() {
        if (!this.currentConsistencyData) {
            this.showError('请先计算一致性分析');
            return;
        }
        
        const data = this.currentConsistencyData;
        let csvContent = "音频文件,V值一致,A值一致,情感类型一致,离散情感一致,患者状态一致,用户V值,用户A值,用户情感类型,用户离散情感,用户患者状态,标准V值,标准A值,标准情感类型,标准离散情感,标准患者状态\n";
        
        data.detailed_results.forEach(result => {
            csvContent += [
                result.audio_file,
                result.v_consistent ? '是' : '否',
                result.a_consistent ? '是' : '否',
                result.emotion_type_consistent ? '是' : '否',
                result.discrete_consistent ? '是' : '否',
                result.patient_consistent ? '是' : '否',
                result.user_values.v_value || '',
                result.user_values.a_value || '',
                result.user_values.emotion_type || '',
                result.user_values.discrete_emotion || '',
                result.user_values.patient_status || '',
                result.standard_values.v_value || '',
                result.standard_values.a_value || '',
                result.standard_values.emotion_type || '',
                result.standard_values.discrete_emotion || '',
                result.standard_values.patient_status || ''
            ].join(',') + '\n';
        });
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `consistency_report_${data.username}_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        this.showSuccess('一致性报告已导出');
    }

    /**
     * 生成详细一致性报告
     */
    generateDetailedConsistencyReport() {
        if (!this.currentConsistencyData) {
            this.showError('请先计算一致性分析');
            return;
        }

        const data = this.currentConsistencyData;
        const reportDiv = document.getElementById('detailed-consistency-report');
        
        let reportHtml = `
            <div class="detailed-report-content">
                <h4>用户 ${data.username} 的详细一致性报告</h4>
                <div class="report-summary">
                    <p><strong>报告生成时间:</strong> ${new Date().toLocaleString()}</p>
                    <p><strong>总样本数:</strong> ${data.total_samples}</p>
                    <p><strong>总体一致性:</strong> ${data.overall_consistency.toFixed(2)}%</p>
                </div>
                
                <div class="detailed-results">
                    <h5>详细结果列表</h5>
                    <table class="detailed-results-table">
                        <thead>
                            <tr>
                                <th>音频文件</th>
                                <th>V值一致</th>
                                <th>A值一致</th>
                                <th>情感类型一致</th>
                                <th>离散情感一致</th>
                                <th>患者状态一致</th>
                                <th>用户标注</th>
                                <th>标准答案</th>
                            </tr>
                        </thead>
                        <tbody>
        `;
        
        data.detailed_results.forEach(result => {
            reportHtml += `
                <tr class="${result.v_consistent && result.a_consistent && result.emotion_type_consistent && result.discrete_consistent && result.patient_consistent ? 'consistent-row' : 'inconsistent-row'}">
                    <td>${result.audio_file}</td>
                    <td class="${result.v_consistent ? 'consistent' : 'inconsistent'}">${result.v_consistent ? '✓' : '✗'}</td>
                    <td class="${result.a_consistent ? 'consistent' : 'inconsistent'}">${result.a_consistent ? '✓' : '✗'}</td>
                    <td class="${result.emotion_type_consistent ? 'consistent' : 'inconsistent'}">${result.emotion_type_consistent ? '✓' : '✗'}</td>
                    <td class="${result.discrete_consistent ? 'consistent' : 'inconsistent'}">${result.discrete_consistent ? '✓' : '✗'}</td>
                    <td class="${result.patient_consistent ? 'consistent' : 'inconsistent'}">${result.patient_consistent ? '✓' : '✗'}</td>
                    <td>
                        V: ${result.user_values.v_value || 'N/A'}<br>
                        A: ${result.user_values.a_value || 'N/A'}<br>
                        情感: ${result.user_values.emotion_type || 'N/A'}<br>
                        离散: ${result.user_values.discrete_emotion || 'N/A'}<br>
                        状态: ${result.user_values.patient_status || 'N/A'}
                    </td>
                    <td>
                        V: ${result.standard_values.v_value || 'N/A'}<br>
                        A: ${result.standard_values.a_value || 'N/A'}<br>
                        情感: ${result.standard_values.emotion_type || 'N/A'}<br>
                        离散: ${result.standard_values.discrete_emotion || 'N/A'}<br>
                        状态: ${result.standard_values.patient_status || 'N/A'}
                    </td>
                </tr>
            `;
        });
        
        reportHtml += `
                        </tbody>
                    </table>
                </div>
                
                <div class="export-options">
                    <button class="btn btn-primary" onclick="adminDashboard.exportConsistencyAsCSV()">导出为CSV</button>
                    <button class="btn btn-primary" onclick="adminDashboard.exportConsistencyAsJSON()">导出为JSON</button>
                </div>
            </div>
        `;
        
        reportDiv.innerHTML = reportHtml;
        reportDiv.style.display = 'block';
        
        this.showSuccess('详细报告已生成');
    }

    /**
     * 导出一致性数据为CSV格式
     */
    exportConsistencyAsCSV() {
        if (!this.currentConsistencyData) {
            this.showError('请先计算一致性分析');
            return;
        }
        
        const data = this.currentConsistencyData;
        let csvContent = "音频文件,V值一致,A值一致,情感类型一致,离散情感一致,患者状态一致,用户V值,用户A值,用户情感类型,用户离散情感,用户患者状态,标准V值,标准A值,标准情感类型,标准离散情感,标准患者状态\n";
        
        data.detailed_results.forEach(result => {
            csvContent += [
                result.audio_file,
                result.v_consistent ? '是' : '否',
                result.a_consistent ? '是' : '否',
                result.emotion_type_consistent ? '是' : '否',
                result.discrete_consistent ? '是' : '否',
                result.patient_consistent ? '是' : '否',
                result.user_values.v_value || '',
                result.user_values.a_value || '',
                result.user_values.emotion_type || '',
                result.user_values.discrete_emotion || '',
                result.user_values.patient_status || '',
                result.standard_values.v_value || '',
                result.standard_values.a_value || '',
                result.standard_values.emotion_type || '',
                result.standard_values.discrete_emotion || '',
                result.standard_values.patient_status || ''
            ].join(',') + '\n';
        });
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `consistency_report_${data.username}_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        this.showSuccess('CSV报告已导出');
    }

    /**
     * 导出一致性数据为JSON格式
     */
    exportConsistencyAsJSON() {
        if (!this.currentConsistencyData) {
            this.showError('请先计算一致性分析');
            return;
        }
        
        const data = this.currentConsistencyData;
        const exportData = {
            username: data.username,
            export_time: new Date().toISOString(),
            total_samples: data.total_samples,
            overall_consistency: data.overall_consistency,
            consistency_scores: data.consistency_scores,
            consistency_percentages: data.consistency_percentages,
            detailed_results: data.detailed_results
        };
        
        const jsonContent = JSON.stringify(exportData, null, 2);
        const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `consistency_report_${data.username}_${new Date().toISOString().split('T')[0]}.json`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        this.showSuccess('JSON报告已导出');
    }

    /**
     * 加载测试设置数据
     */
    async loadTestSettingsData() {
        try {
            const response = await fetch('/admin/api/users/test-settings');
            const data = await response.json();

            if (response.ok) {
                this.updateTestSettingsTable(data.users);
            } else {
                this.showError('加载测试设置数据失败: ' + data.error);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    /**
     * 更新测试设置表格
     * @param {Array} users - 用户数据数组
     */
    updateTestSettingsTable(users) {
        const tbody = document.getElementById('test-settings-tbody');
        tbody.innerHTML = '';

        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.wechat_name}</td>
                <td>${user.phone_number}</td>
                <td>${new Date(user.created_at).toLocaleDateString()}</td>
                <td>
                    <label class="switch">
                        <input type="checkbox" ${user.skip_test ? 'checked' : ''} 
                               onchange="adminDashboard.updateTestSetting('${user.wechat_name}', 'skip_test', this.checked)">
                        <span class="slider"></span>
                    </label>
                </td>
                <td>
                    <label class="switch">
                        <input type="checkbox" ${user.skip_consistency_test ? 'checked' : ''} 
                               onchange="adminDashboard.updateTestSetting('${user.wechat_name}', 'skip_consistency_test', this.checked)">
                        <span class="slider"></span>
                    </label>
                </td>
                <td>
                    <button class="btn btn-sm btn-secondary" 
                            onclick="adminDashboard.resetUserTestSettings('${user.wechat_name}')">
                        重置
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    /**
     * 更新用户测试设置
     * @param {string} username - 用户名
     * @param {string} setting - 设置类型
     * @param {boolean} value - 设置值
     */
    async updateTestSetting(username, setting, value) {
        try {
            const requestData = {
                username: username
            };
            requestData[setting] = value;

            const response = await fetch('/admin/api/users/test-settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            if (response.ok) {
                this.showSuccess(data.message);
            } else {
                this.showError('更新失败: ' + data.message);
                // 恢复开关状态
                this.loadTestSettingsData();
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
            // 恢复开关状态
            this.loadTestSettingsData();
        }
    }

    /**
     * 重置用户测试设置
     * @param {string} username - 用户名
     */
    async resetUserTestSettings(username) {
        if (!confirm(`确定要重置用户 ${username} 的测试设置吗？这将要求用户重新进行测试和一致性检验。`)) {
            return;
        }

        try {
            const response = await fetch('/admin/api/users/test-settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    skip_test: false,
                    skip_consistency_test: false
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.showSuccess('用户测试设置已重置');
                this.loadTestSettingsData();
            } else {
                this.showError('重置失败: ' + data.message);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    /**
     * 加载管理员数据
     */
    async loadAdminsData() {
        console.log('loadAdminsData called');
        try {
            const response = await fetch('/admin/api/admins');
            console.log('API response status:', response.status);
            const data = await response.json();
            console.log('API response data:', data);

            if (response.ok) {
                this.updateAdminsTable(data.admins);
                this.updateAdminPermissions(data.current_admin);
            } else {
                console.error('API error:', data.error);
                this.showError('加载管理员数据失败: ' + data.error);
            }
        } catch (error) {
            console.error('Network error:', error);
            this.showError('网络错误: ' + error.message);
        }
    }

    /**
     * 更新管理员表格
     * @param {Array} admins - 管理员列表
     */
    updateAdminsTable(admins) {
        const tbody = document.querySelector('#admins-table tbody');
        tbody.innerHTML = '';

        admins.forEach(admin => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${admin.id}</td>
                <td>${admin.username}</td>
                <td>
                    <span class="role-badge ${admin.role}">
                        ${admin.role === 'super_admin' ? '超级管理员' : '普通管理员'}
                    </span>
                </td>
                <td>${admin.description || '-'}</td>
                <td>
                    <span class="status-badge ${admin.is_active ? 'active' : 'inactive'}">
                        ${admin.is_active ? '激活' : '禁用'}
                    </span>
                </td>
                <td>${new Date(admin.created_at).toLocaleString()}</td>
                <td>
                    ${admin.role !== 'super_admin' ? `
                        <button class="btn btn-sm btn-warning" onclick="adminDashboard.toggleAdminStatus(${admin.id}, ${!admin.is_active})">
                            ${admin.is_active ? '禁用' : '激活'}
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="adminDashboard.deleteAdmin(${admin.id}, '${admin.username}')">
                            删除
                        </button>
                    ` : '<span class="text-muted">-</span>'}
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    /**
     * 更新管理员权限显示
     * @param {Object} currentAdmin - 当前管理员信息
     */
    updateAdminPermissions(currentAdmin) {
        console.log('updateAdminPermissions called with:', currentAdmin);
        const createBtn = document.getElementById('create-admin-btn');
        if (!createBtn) {
            console.error('create-admin-btn element not found');
            return;
        }
        
        if (currentAdmin && currentAdmin.role === 'super_admin') {
            console.log('Showing create admin button for super admin');
            createBtn.style.display = 'inline-block';
        } else {
            console.log('Hiding create admin button, role:', currentAdmin ? currentAdmin.role : 'no admin data');
            createBtn.style.display = 'none';
        }
    }

    /**
     * 显示创建管理员模态框
     */
    showCreateAdminModal() {
        document.getElementById('create-admin-modal').style.display = 'block';
        document.getElementById('create-admin-form').reset();
    }

    /**
     * 创建管理员
     */
    async createAdmin() {
        const form = document.getElementById('create-admin-form');
        const formData = new FormData(form);
        
        const adminData = {
            username: formData.get('username'),
            password: formData.get('password'),
            description: formData.get('description')
        };

        try {
            const response = await fetch('/admin/api/admins', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(adminData)
            });

            const data = await response.json();

            if (response.ok) {
                this.showSuccess(data.message);
                document.getElementById('create-admin-modal').style.display = 'none';
                this.loadAdminsData();
            } else {
                this.showError('创建失败: ' + data.message);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    /**
     * 显示修改密码模态框
     */
    showChangePasswordModal() {
        document.getElementById('change-password-modal').style.display = 'block';
        document.getElementById('change-password-form').reset();
    }

    /**
     * 修改管理员密码
     */
    async changePassword() {
        const form = document.getElementById('change-password-form');
        const formData = new FormData(form);
        
        const newPassword = formData.get('new_password');
        const confirmPassword = formData.get('confirm_password');
        
        if (newPassword !== confirmPassword) {
            this.showError('新密码和确认密码不匹配');
            return;
        }

        const passwordData = {
            old_password: formData.get('old_password'),
            new_password: newPassword
        };

        try {
            const response = await fetch('/admin/api/admins/change-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(passwordData)
            });

            const data = await response.json();

            if (response.ok) {
                this.showSuccess(data.message);
                document.getElementById('change-password-modal').style.display = 'none';
            } else {
                this.showError('修改失败: ' + data.message);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    /**
     * 切换管理员状态
     * @param {number} adminId - 管理员ID
     * @param {boolean} isActive - 新状态
     */
    async toggleAdminStatus(adminId, isActive) {
        try {
            const response = await fetch(`/admin/api/admins/${adminId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ is_active: isActive })
            });

            const data = await response.json();

            if (response.ok) {
                this.showSuccess(data.message);
                this.loadAdminsData();
            } else {
                this.showError('更新失败: ' + data.message);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    /**
     * 删除管理员
     * @param {number} adminId - 管理员ID
     * @param {string} username - 管理员用户名
     */
    async deleteAdmin(adminId, username) {
        if (!confirm(`确定要删除管理员 "${username}" 吗？此操作不可撤销。`)) {
            return;
        }

        try {
            const response = await fetch(`/admin/api/admins/${adminId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (response.ok) {
                this.showSuccess(data.message);
                this.loadAdminsData();
            } else {
                this.showError('删除失败: ' + data.message);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }
}

// 全局函数，用于模态框关闭
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// 初始化管理员仪表板
let adminDashboard;
document.addEventListener('DOMContentLoaded', () => {
    adminDashboard = new AdminDashboard();
});