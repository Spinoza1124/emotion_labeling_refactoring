/**
 * 音频列表管理器模块
 * 负责管理说话人选择和音频列表显示
 */
class AudioListManager {
    constructor(speakerSelect, audioListContainer) {
        this.speakerSelect = speakerSelect;
        this.audioListContainer = audioListContainer;
        this.currentSpeaker = null;
        this.audioList = [];
        this.currentAudioIndex = -1;
        this.onAudioSelectCallback = null;
        
        this.initEventListeners();
    }

    /**
     * 初始化事件监听器
     */
    initEventListeners() {
        this.speakerSelect.addEventListener('change', (e) => {
            this.handleSpeakerChange(e.target.value);
        });
    }

    /**
     * 初始化说话人列表
     */
    async initSpeakers(username) {
        try {
            const response = await fetch(`/api/speakers/${encodeURIComponent(username)}`);
            const speakers = await response.json();
            
            this.speakerSelect.innerHTML = '<option value="">请选择说话人</option>';
            speakers.forEach(speaker => {
                const option = document.createElement('option');
                option.value = speaker;
                option.textContent = speaker;
                this.speakerSelect.appendChild(option);
            });
        } catch (error) {
            console.error('加载说话人列表失败:', error);
        }
    }

    /**
     * 处理说话人选择变化
     */
    async handleSpeakerChange(speaker) {
        if (!speaker) {
            this.clearAudioList();
            return;
        }
        
        this.currentSpeaker = speaker;
        await this.loadAudioList(speaker);
    }

    /**
     * 加载音频列表
     */
    async loadAudioList(speaker) {
        try {
            const username = window.userManager?.getCurrentUsername();
            if (!username) {
                console.error('用户未登录');
                return;
            }
            
            const response = await fetch(`/api/audio_list/${encodeURIComponent(username)}/${encodeURIComponent(speaker)}`);
            const audioList = await response.json();
            
            this.audioList = audioList;
            this.renderAudioList();
        } catch (error) {
            console.error('加载音频列表失败:', error);
        }
    }

    /**
     * 渲染音频列表
     */
    renderAudioList() {
        this.audioListContainer.innerHTML = '';
        
        this.audioList.forEach((audio, index) => {
            const audioItem = document.createElement('div');
            audioItem.className = 'audio-item';
            
            // 根据标注完整性设置样式类
            const completeness = audio.annotation_completeness || 'none';
            if (completeness === 'va-only') {
                audioItem.classList.add('labeled-va');
            } else if (completeness === 'complete') {
                audioItem.classList.add('labeled-complete');
            }
            // 如果是 'none'，则不添加任何特殊样式类，保持默认颜色
            
            audioItem.innerHTML = `
                <span class="audio-name">${audio.file_name}</span>
            `;
            
            audioItem.addEventListener('click', () => {
                this.selectAudio(index);
            });
            
            this.audioListContainer.appendChild(audioItem);
        });
    }

    /**
     * 选择音频
     */
    selectAudio(index) {
        if (index < 0 || index >= this.audioList.length) {
            return;
        }
        
        this.currentAudioIndex = index;
        this.updateAudioSelection();
        
        if (this.onAudioSelectCallback) {
            this.onAudioSelectCallback(this.audioList[index], index);
        }
    }

    /**
     * 更新音频选择状态
     */
    updateAudioSelection() {
        const audioItems = this.audioListContainer.querySelectorAll('.audio-item');
        audioItems.forEach((item, index) => {
            item.classList.toggle('selected', index === this.currentAudioIndex);
        });
    }

    /**
     * 设置音频选择回调
     */
    setOnAudioSelectCallback(callback) {
        this.onAudioSelectCallback = callback;
    }

    /**
     * 获取当前音频
     */
    getCurrentAudio() {
        if (this.currentAudioIndex >= 0 && this.currentAudioIndex < this.audioList.length) {
            return this.audioList[this.currentAudioIndex];
        }
        return null;
    }

    /**
     * 获取音频列表
     */
    getAudioList() {
        return this.audioList;
    }

    /**
     * 下一个音频
     */
    nextAudio() {
        if (this.currentAudioIndex < this.audioList.length - 1) {
            this.selectAudio(this.currentAudioIndex + 1);
        }
    }

    /**
     * 上一个音频
     */
    previousAudio() {
        if (this.currentAudioIndex > 0) {
            this.selectAudio(this.currentAudioIndex - 1);
        }
    }

    /**
     * 更新音频标注状态
     */
    updateAudioLabelStatus(index, labeled) {
        if (index >= 0 && index < this.audioList.length) {
            this.audioList[index].labeled = labeled;
            this.renderAudioList();
            this.updateAudioSelection();
        }
    }

    /**
     * 清空音频列表
     */
    clearAudioList() {
        this.audioList = [];
        this.currentAudioIndex = -1;
        this.audioListContainer.innerHTML = '';
        this.currentSpeaker = null;
    }
}

