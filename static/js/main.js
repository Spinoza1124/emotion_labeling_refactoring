/**
 * 音频情感标注系统主文件（重构版）
 * 负责协调各个模块的工作
 */

class EmotionLabelingApp {
    constructor() {
        this.userManager = null;
        this.audioPlayer = null;
        this.audioListManager = null;
        this.emotionAnnotator = null;
        this.keyboardHandler = null;
        
        this.initApp();
    }

    async initApp() {
        // 初始化用户管理
        this.userManager = new UserManager();
        if (!this.userManager.initAuth()) {
            return; // 用户未登录，已跳转
        }
        
        // 设置为全局变量，供其他模块使用
        window.userManager = this.userManager;

        // 获取DOM元素
        const elements = this.getDOMElements();
        
        // 初始化各个模块
        this.initModules(elements);
        
        // 设置事件监听
        this.setupEventListeners(elements);
        
        // 初始化说话人列表
        try {
            await this.audioListManager.initSpeakers(this.userManager.getCurrentUsername());
        } catch (error) {
            console.error('初始化说话人列表失败:', error);
        }
        
        // 更新用户显示
        elements.currentUserSpan.textContent = this.userManager.getCurrentUsername();
    }

    getDOMElements() {
        return {
            // 主界面元素
            mainContainer: document.getElementById('main-container'),
            currentUserSpan: document.getElementById('current-user'),
            logoutButton: document.getElementById('logout-button'),
            
            // 音频相关元素
            speakerSelect: document.getElementById('speaker-select'),
            audioListContainer: document.getElementById('audio-list-container'),
            audioPlayer: document.getElementById('audio-player'),
            loopCheckbox: document.getElementById('loop-checkbox'),
            playCountValue: document.getElementById('play-count-value'),
            
            // 标注相关元素
            vSlider: document.getElementById('v-slider'),
            aSlider: document.getElementById('a-slider'),
            vValue: document.getElementById('v-value'),
            aValue: document.getElementById('a-value'),
            
            // 情感类型元素
            neutralType: document.getElementById('neutral-type'),
            nonNeutralType: document.getElementById('non-neutral-type'),
            specificEmotions: document.getElementById('specific-emotions'),
            emotionTypeRadios: document.querySelectorAll('input[name="emotion-type"]'),
            
            // 患者状态和离散情感
            patientRadios: document.querySelectorAll('input[name="patient-status"]'),
            discreteEmotionRadios: document.querySelectorAll('input[name="discrete-emotion"]'),
            
            // 按钮元素
            saveButton: document.getElementById('save-button'),
            nextButton: document.getElementById('next-button'),
            continueButton: document.getElementById('continue-button'),
            backButton: document.getElementById('back-button'),
            prevButton: document.getElementById('prev-button'),
            
            // 标注模式区域
            vaLabeling: document.getElementById('va-labeling'),
            discreteLabeling: document.getElementById('discrete-labeling')
        };
    }

    initModules(elements) {
        // 初始化音频播放器
        this.audioPlayer = new AudioPlayer(elements.audioPlayer, elements.playCountValue);
        
        // 初始化音频列表管理器
        this.audioListManager = new AudioListManager(elements.speakerSelect, elements.audioListContainer);
        
        // 初始化情感标注器
        this.emotionAnnotator = new EmotionAnnotator(elements);
        
        // 初始化键盘处理器
        this.keyboardHandler = new KeyboardHandler({
            togglePlayPause: () => this.audioPlayer.togglePlayPause(),
            previous: () => this.handlePrevious(),
            next: () => this.handleNext(),
            save: () => this.handleSave(),
            continueOrBack: () => this.handleContinueOrBack()
        });
    }

    setupEventListeners(elements) {
        // 退出登录
        elements.logoutButton.addEventListener('click', () => {
            this.userManager.logout();
        });
        
        // 循环播放
        elements.loopCheckbox.addEventListener('change', () => {
            this.audioPlayer.setLoop(elements.loopCheckbox.checked);
        });
        
        // 音频选择回调
        this.audioListManager.setOnAudioSelectCallback((audioFile, index) => {
            this.handleAudioSelect(audioFile, index);
        });
        
        // 按钮事件
        elements.saveButton.addEventListener('click', () => this.handleSave());
        elements.nextButton.addEventListener('click', () => this.handleNext());
        elements.continueButton.addEventListener('click', () => this.handleContinue());
        elements.backButton.addEventListener('click', () => this.handleBack());
        elements.prevButton.addEventListener('click', () => this.handlePrevious());
    }

    async handleAudioSelect(audioFile, index) {
        // 检查是否有未保存的修改
        if (this.emotionAnnotator.getModified()) {
            if (!confirm('当前标注未保存，是否继续？')) {
                return;
            }
        }
        
        // 加载音频
        try {
            await this.audioPlayer.loadAudio(
                audioFile, 
                this.audioListManager.currentSpeaker, 
                this.userManager.getCurrentUsername()
            );
        } catch (error) {
            console.error('加载音频失败:', error);
        }
        
        // 重置标注并切换到VA模式
        this.emotionAnnotator.reset();
        this.emotionAnnotator.switchToVaMode();
        
        // 更新按钮状态
        this.updateButtonStates();
        
        // 如果有已保存的标注，加载它
        if (audioFile.labeled) {
            try {
                await this.emotionAnnotator.loadSavedLabel(
                    this.userManager.getCurrentUsername(),
                    this.audioListManager.currentSpeaker,
                    audioFile.file_name
                );
                this.updateSaveButtonStatus(true);
            } catch (error) {
                console.error('加载已保存标注失败:', error);
            }
        }
        
        this.keyboardHandler.resetFocus();
    }

    async handleSave() {
        const currentAudio = this.audioListManager.getCurrentAudio();
        if (!currentAudio) return;
        
        const annotation = this.emotionAnnotator.getCurrentAnnotation();
        const labelData = {
            speaker: this.audioListManager.currentSpeaker,
            audio_file: currentAudio.file_name,
            username: this.userManager.getCurrentUsername(),
            ...annotation
        };
        
        const saveButton = document.getElementById('save-button');
        saveButton.disabled = true;
        saveButton.textContent = '保存中...';
        
        try {
            const result = await DataService.saveLabel(labelData);
            if (result.success) {
                const completeness = this.emotionAnnotator.getAnnotationCompleteness();
                this.audioListManager.updateAudioLabelStatus(
                    this.audioListManager.currentAudioIndex, 
                    true, 
                    completeness
                );
                this.emotionAnnotator.setModified(false);
                this.updateSaveButtonStatus(true);
            } else {
                throw new Error(result.error || '保存失败');
            }
        } catch (error) {
            console.error('保存标注失败:', error);
            alert('保存标注失败，请重试');
            saveButton.textContent = '保存(W)';
            saveButton.disabled = false;
        }
        
        this.keyboardHandler.resetFocus();
    }

    handleNext() {
        if (this.emotionAnnotator.getModified()) {
            if (!confirm('当前标注未保存，是否继续？')) {
                return;
            }
        }
        
        this.audioListManager.nextAudio();
        this.keyboardHandler.resetFocus();
    }

    handlePrevious() {
        if (this.emotionAnnotator.getModified()) {
            if (!confirm('当前标注未保存，是否继续？')) {
                return;
            }
        }
        
        this.audioListManager.previousAudio();
        this.keyboardHandler.resetFocus();
    }

    handleContinue() {
        if (this.emotionAnnotator.getModified() && this.emotionAnnotator.isVaLabelingMode) {
            if (!confirm('VA标注已修改但未保存，是否继续？可以先点保存，再继续')) {
                return;
            }
        }
        
        this.emotionAnnotator.switchToDiscreteMode();
        this.keyboardHandler.resetFocus();
    }

    handleBack() {
        if (this.emotionAnnotator.getModified() && !this.emotionAnnotator.isVaLabelingMode) {
            if (!confirm('离散情感标注未保存，是否返回VA标注？')) {
                return;
            }
        }
        
        this.emotionAnnotator.switchToVaMode();
        this.keyboardHandler.resetFocus();
    }

    handleContinueOrBack() {
        if (this.emotionAnnotator.isVaLabelingMode) {
            this.handleContinue();
        } else {
            this.handleBack();
        }
    }

    updateButtonStates() {
        const audioList = this.audioListManager.getAudioList();
        const currentIndex = this.audioListManager.currentAudioIndex;
        
        document.getElementById('prev-button').disabled = currentIndex <= 0;
        document.getElementById('next-button').disabled = currentIndex >= audioList.length - 1;
        document.getElementById('continue-button').disabled = false;
        document.getElementById('save-button').disabled = false;
    }

    updateSaveButtonStatus(isSaved = false) {
        const saveButton = document.getElementById('save-button');
        saveButton.classList.remove('saved-va', 'saved-complete');
        
        if (isSaved) {
            const completeness = this.emotionAnnotator.getAnnotationCompleteness();
            
            if (completeness === 'complete') {
                saveButton.textContent = '已保存(W)';
                saveButton.classList.add('saved-complete');
                saveButton.disabled = true;
            } else if (completeness === 'va-only') {
                saveButton.textContent = '已保存(W)';
                saveButton.classList.add('saved-va');
                saveButton.disabled = true;
            } else {
                saveButton.textContent = '保存(W)';
                saveButton.disabled = false;
            }
        } else {
            saveButton.textContent = '保存(W)';
            saveButton.disabled = false;
        }
    }
}

// 当DOM加载完成时初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new EmotionLabelingApp();
});