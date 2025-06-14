/**
 * 音频播放器模块
 * 负责音频播放控制和播放计数
 */
class AudioPlayer {
    constructor(audioElement, playCountElement) {
        this.audioElement = audioElement;
        this.playCountElement = playCountElement;
        this.currentPlayCount = 0;
        this.currentAudioFile = null;
        this.currentSpeaker = null;
        this.currentUsername = null;
        
        this.initEventListeners();
    }

    initEventListeners() {
        this.audioElement.addEventListener('loadedmetadata', () => {
            const duration = this.audioElement.duration;
            console.log(`音频时长: ${duration.toFixed(2)}秒`);
        });
    }

    /**
     * 播放/暂停切换
     */
    togglePlayPause() {
        if (this.audioElement.src) {
            if (this.audioElement.paused) {
                this.audioElement.play();
            } else {
                this.audioElement.pause();
            }
        }
    }

    /**
     * 加载音频文件
     */
    loadAudio(audioFile, speaker, username) {
        this.currentAudioFile = audioFile;
        this.currentSpeaker = speaker;
        this.currentUsername = username;
        
        this.audioElement.src = audioFile.path;
        this.audioElement.load();
        
        // 移除之前的播放结束事件监听器
        this.audioElement.removeEventListener('ended', this.handleAudioEnded);
        
        // 添加播放结束事件监听器
        this.handleAudioEnded = () => {
            this.incrementPlayCount();
        };
        
        this.audioElement.addEventListener('ended', this.handleAudioEnded);
        
        // 等待音频元数据加载完成后再加载播放次数
        this.audioElement.addEventListener('loadedmetadata', () => {
            this.loadPlayCount();
        }, { once: true });
        
        // 不自动播放，让用户手动控制
        return Promise.resolve();
    }

    /**
     * 增加播放次数（音频播放完成后调用）
     */
    incrementPlayCount() {
        if (!this.currentAudioFile || !this.currentSpeaker || !this.currentUsername) {
            return;
        }
        
        const requestData = {
            username: this.currentUsername,
            speaker: this.currentSpeaker,
            audio_file: this.currentAudioFile.file_name
        };
        
        fetch('/api/save_play_count', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.currentPlayCount = data.play_count;
                this.updatePlayCountDisplay();
            }
        })
        .catch(error => {
            console.error('保存播放计数失败:', error);
        });
    }

    /**
     * 加载播放次数
     */
    loadPlayCount() {
        console.log('开始加载播放次数:', {
            username: this.currentUsername,
            speaker: this.currentSpeaker,
            audioFile: this.currentAudioFile?.file_name
        });
        
        if (!this.currentUsername || !this.currentSpeaker || !this.currentAudioFile) {
            console.log('缺少必要参数，设置播放次数为0');
            this.currentPlayCount = 0;
            this.updatePlayCountDisplay();
            return;
        }
        
        const url = `/api/get_play_count/${encodeURIComponent(this.currentUsername)}/${encodeURIComponent(this.currentSpeaker)}/${encodeURIComponent(this.currentAudioFile.file_name)}`;
        console.log('请求URL:', url);
        
        fetch(url)
            .then(response => {
                console.log('API响应状态:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('API响应数据:', data);
                if (data.success) {
                    this.currentPlayCount = data.play_count || 0;
                    console.log('设置播放次数为:', this.currentPlayCount);
                    this.updatePlayCountDisplay();
                } else {
                    console.log('API返回失败，设置播放次数为0');
                    this.currentPlayCount = 0;
                    this.updatePlayCountDisplay();
                }
            })
            .catch(error => {
                console.error('获取播放计数失败:', error);
                this.currentPlayCount = 0;
                this.updatePlayCountDisplay();
            });
    }

    /**
     * 更新播放次数显示
     */
    updatePlayCountDisplay() {
        console.log('更新播放次数显示:', this.currentPlayCount);
        if (this.playCountElement) {
            this.playCountElement.textContent = this.currentPlayCount;
            console.log('播放次数元素已更新，当前文本:', this.playCountElement.textContent);
        } else {
            console.error('播放次数显示元素未找到');
        }
    }

    /**
     * 重置播放器
     */
    reset() {
        this.audioElement.src = '';
        this.currentPlayCount = 0;
        this.updatePlayCountDisplay();
    }
}

