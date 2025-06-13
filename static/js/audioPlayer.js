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
        
        // 加载播放次数
        this.loadPlayCount();
        
        // 移除之前的播放事件监听器
        this.audioElement.removeEventListener('play', this.handleAudioPlay);
        
        // 添加新的播放事件监听器
        this.handleAudioPlay = () => {
            this.incrementPlayCount();
        };
        
        this.audioElement.addEventListener('play', this.handleAudioPlay);
        
        return this.audioElement.play();
    }

    /**
     * 设置循环播放
     */
    setLoop(loop) {
        this.audioElement.loop = loop;
    }

    /**
     * 增加播放次数
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
        if (!this.currentUsername || !this.currentSpeaker || !this.currentAudioFile) {
            this.currentPlayCount = 0;
            this.updatePlayCountDisplay();
            return;
        }
        
        fetch(`/api/get_play_count/${encodeURIComponent(this.currentUsername)}/${encodeURIComponent(this.currentSpeaker)}/${encodeURIComponent(this.currentAudioFile.file_name)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.currentPlayCount = data.play_count || 0;
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
        if (this.playCountElement) {
            this.playCountElement.textContent = this.currentPlayCount;
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

