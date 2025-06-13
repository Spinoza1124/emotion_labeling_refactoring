/**
 * 情感标注模块
 * 负责VA值标注和离散情感标注
 */
class EmotionAnnotator {
    constructor(elements) {
        this.elements = elements;
        this.isModified = false;
        this.isVaLabelingMode = true;
        this.emotionType = 'neutral';
        this.selectedDiscreteEmotion = null;
        this.patientStatus = 'patient';
        
        this.initElements();
        this.initEventListeners();
    }

    initElements() {
        // 初始化滑动条默认值
        this.elements.vSlider.min = -2;
        this.elements.vSlider.max = 2;
        this.elements.vSlider.step = 0.5;
        this.elements.vSlider.value = 0;

        this.elements.aSlider.min = 1;
        this.elements.aSlider.max = 5;
        this.elements.aSlider.step = 0.5;
        this.elements.aSlider.value = 3;

        // 更新显示值
        this.updateSliderDisplay();
    }

    initEventListeners() {
        // VA滑动条事件
        this.elements.vSlider.addEventListener('input', (e) => this.handleSliderChange(e));
        this.elements.aSlider.addEventListener('input', (e) => this.handleSliderChange(e));
        
        // 患者状态事件
        this.elements.patientRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                this.patientStatus = radio.value;
                this.setModified(true);
            });
        });
        
        // 情感类型事件
        this.elements.emotionTypeRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                this.emotionType = radio.value;
                this.handleEmotionTypeChange();
                this.setModified(true);
            });
        });
        
        // 离散情感事件
        this.elements.discreteEmotionRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                this.selectedDiscreteEmotion = radio.value;
                this.setModified(true);
            });
        });
    }

    /**
     * 处理滑动条变化
     */
    handleSliderChange(event) {
        const slider = event.target;
        const valueElement = slider.id === 'v-slider' ? this.elements.vValue : this.elements.aValue;
        valueElement.textContent = Number(slider.value).toFixed(2);
        this.setModified(true);
    }

    /**
     * 更新滑动条显示
     */
    updateSliderDisplay() {
        this.elements.vValue.textContent = Number(this.elements.vSlider.value).toFixed(2);
        this.elements.aValue.textContent = Number(this.elements.aSlider.value).toFixed(2);
    }

    /**
     * 处理情感类型变化
     */
    handleEmotionTypeChange() {
        if (this.emotionType === 'non-neutral') {
            this.elements.specificEmotions.style.display = 'block';
        } else {
            this.elements.specificEmotions.style.display = 'none';
            this.selectedDiscreteEmotion = null;
            // 清除所有具体情感的选择
            this.elements.discreteEmotionRadios.forEach(radio => {
                radio.checked = false;
            });
        }
    }

    /**
     * 切换到VA标注模式
     */
    switchToVaMode() {
        this.isVaLabelingMode = true;
        this.elements.vaLabeling.style.display = 'block';
        this.elements.discreteLabeling.style.display = 'none';
        this.elements.continueButton.style.display = 'inline-block';
        this.elements.backButton.style.display = 'none';
    }

    /**
     * 切换到离散情感标注模式
     */
    switchToDiscreteMode() {
        this.isVaLabelingMode = false;
        this.elements.vaLabeling.style.display = 'none';
        this.elements.discreteLabeling.style.display = 'block';
        this.elements.continueButton.style.display = 'none';
        this.elements.backButton.style.display = 'inline-block';
        this.setModified(false);
    }

    /**
     * 加载已保存的标注数据
     */
    loadSavedLabel(username, speaker, filename) {
        return fetch(`/api/get_label/${encodeURIComponent(username)}/${encodeURIComponent(speaker)}/${encodeURIComponent(filename)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.data) {
                    const label = data.data;
                    
                    // 设置VA值
                    if (label.v_value !== undefined) {
                        this.elements.vSlider.value = label.v_value;
                    }
                    if (label.a_value !== undefined) {
                        this.elements.aSlider.value = label.a_value;
                    }
                    this.updateSliderDisplay();
                    
                    // 设置患者状态
                    if (label.patient_status) {
                        this.patientStatus = label.patient_status;
                        const patientRadio = document.getElementById(label.patient_status === 'patient' ? 'is-patient' : 'not-patient');
                        if (patientRadio) patientRadio.checked = true;
                    }
                    
                    // 设置情感类型
                    if (label.emotion_type) {
                        this.emotionType = label.emotion_type;
                        const emotionRadio = document.getElementById(label.emotion_type === 'neutral' ? 'neutral-type' : 'non-neutral-type');
                        if (emotionRadio) emotionRadio.checked = true;
                        
                        this.handleEmotionTypeChange();
                        
                        // 设置具体情感
                        if (label.discrete_emotion) {
                            this.selectedDiscreteEmotion = label.discrete_emotion;
                            const discreteRadio = document.getElementById(`emotion-${label.discrete_emotion}`);
                            if (discreteRadio) discreteRadio.checked = true;
                        }
                    }
                    
                    this.setModified(false);
                    return label;
                }
            });
    }

    /**
     * 获取当前标注数据
     */
    getCurrentAnnotation() {
        return {
            v_value: parseFloat(this.elements.vSlider.value),
            a_value: parseFloat(this.elements.aSlider.value),
            emotion_type: this.emotionType,
            discrete_emotion: this.emotionType === 'neutral' ? null : this.selectedDiscreteEmotion,
            patient_status: this.patientStatus
        };
    }

    /**
     * 判断标注完整性
     */
    getAnnotationCompleteness() {
        const hasVA = this.elements.vSlider.value !== '0' || this.elements.aSlider.value !== '0';
        const hasPatientStatus = this.patientStatus !== null;
        
        if (this.isVaLabelingMode) {
            return hasVA ? 'va-only' : 'none';
        }
        
        const hasEmotionType = this.emotionType !== null;
        const hasDiscreteEmotion = this.emotionType === 'neutral' || (this.emotionType === 'non-neutral' && this.selectedDiscreteEmotion !== null);
        
        if (!hasVA && !hasPatientStatus && !hasEmotionType) {
            return 'none';
        }
        
        if (hasVA && hasPatientStatus && hasEmotionType && hasDiscreteEmotion) {
            return 'complete';
        }
        
        return 'va-only';
    }

    /**
     * 重置标注
     */
    reset() {
        this.elements.vSlider.value = 0;
        this.elements.aSlider.value = 3;
        this.updateSliderDisplay();
        
        // 重置患者状态
        document.getElementById('is-patient').checked = true;
        document.getElementById('not-patient').checked = false;
        this.patientStatus = 'patient';
        
        // 重置情感类型
        document.getElementById('neutral-type').checked = true;
        document.getElementById('non-neutral-type').checked = false;
        this.emotionType = 'neutral';
        this.elements.specificEmotions.style.display = 'none';
        
        // 重置离散情感
        this.elements.discreteEmotionRadios.forEach(radio => {
            radio.checked = false;
        });
        this.selectedDiscreteEmotion = null;
        
        this.setModified(false);
    }

    /**
     * 设置修改状态
     */
    setModified(modified) {
        this.isModified = modified;
    }

    /**
     * 获取修改状态
     */
    getModified() {
        return this.isModified;
    }
}

