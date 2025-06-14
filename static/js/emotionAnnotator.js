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
        this.elements.vSlider.min = 0;
        this.elements.vSlider.max = 2;
        this.elements.vSlider.step = 0.5;
        // 不设置默认值，让用户主动选择

        this.elements.aSlider.min = 1;
        this.elements.aSlider.max = 5;
        this.elements.aSlider.step = 0.5;
        // 不设置默认值，让用户主动选择

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
                    if (label.v_value !== undefined && label.v_value !== null) {
                        this.elements.vSlider.value = label.v_value;
                    } else {
                        this.elements.vSlider.value = '';
                    }
                    if (label.a_value !== undefined && label.a_value !== null) {
                        this.elements.aSlider.value = label.a_value;
                    } else {
                        this.elements.aSlider.value = '';
                    }
                    this.updateSliderDisplay();
                    
                    // 设置患者状态
                    if (label.patient_status && label.patient_status !== null) {
                        this.patientStatus = label.patient_status;
                        const patientRadio = document.getElementById(label.patient_status === 'patient' ? 'is-patient' : 'not-patient');
                        if (patientRadio) patientRadio.checked = true;
                    } else {
                        this.patientStatus = null;
                        // 清除所有患者状态选择
                        const patientRadios = document.querySelectorAll('input[name="patient-status"]');
                        patientRadios.forEach(radio => radio.checked = false);
                    }
                    
                    // 设置情感类型
                    if (label.emotion_type && label.emotion_type !== null) {
                        this.emotionType = label.emotion_type;
                        const emotionRadio = document.getElementById(label.emotion_type === 'neutral' ? 'neutral-type' : 'non-neutral-type');
                        if (emotionRadio) emotionRadio.checked = true;
                        
                        this.handleEmotionTypeChange();
                        
                        // 设置具体情感
                        if (label.discrete_emotion && label.discrete_emotion !== null) {
                            this.selectedDiscreteEmotion = label.discrete_emotion;
                            const discreteRadio = document.getElementById(`emotion-${label.discrete_emotion}`);
                            if (discreteRadio) discreteRadio.checked = true;
                        } else {
                            this.selectedDiscreteEmotion = null;
                        }
                    } else {
                        this.emotionType = null;
                        this.selectedDiscreteEmotion = null;
                        // 清除所有情感类型选择
                        const emotionRadios = document.querySelectorAll('input[name="emotion-type"]');
                        emotionRadios.forEach(radio => radio.checked = false);
                        // 清除所有具体情感选择
                        const discreteRadios = document.querySelectorAll('input[name="discrete-emotion"]');
                        discreteRadios.forEach(radio => radio.checked = false);
                        this.handleEmotionTypeChange();
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
            v_value: this.elements.vSlider.value === '' ? null : parseFloat(this.elements.vSlider.value),
            a_value: this.elements.aSlider.value === '' ? null : parseFloat(this.elements.aSlider.value),
            emotion_type: this.emotionType,
            discrete_emotion: this.emotionType === 'neutral' ? null : this.selectedDiscreteEmotion,
            patient_status: this.patientStatus
        };
    }

    /**
     * 判断标注完整性
     * 返回格式与后端calculate_annotation_completeness保持一致
     */
    getAnnotationCompleteness() {
        // 检查用户是否实际设置了值（不为空字符串）
        const hasV = this.elements.vSlider.value !== '' && this.elements.vSlider.value !== null;
        const hasA = this.elements.aSlider.value !== '' && this.elements.aSlider.value !== null;
        const hasPatientStatus = this.patientStatus !== null;
        
        const hasEmotionType = this.emotionType !== null;
        const hasDiscreteEmotion = this.emotionType === 'neutral' || (this.emotionType === 'non-neutral' && this.selectedDiscreteEmotion !== null);
        
        // 检查离散情感标注是否完整
        const discreteComplete = hasPatientStatus && hasEmotionType && hasDiscreteEmotion;
        
        // 构建结果数组 - 始终检查所有标注类型的完整性，不受当前模式影响
        const result = [];
        // VA标注完整性：V和A都有值时才算完整
        if (hasV && hasA) result.push('va_complete');
        if (discreteComplete) result.push('discrete_complete');
        
        // 如果什么都没有标注，返回['none']
        if (result.length === 0) {
            return ['none'];
        }
        
        return result;
    }

    /**
     * 重置标注
     */
    reset() {
        // 清空滑块值，不设置默认值
        this.elements.vSlider.value = '';
        this.elements.aSlider.value = '';
        this.updateSliderDisplay();
        
        // 重置患者状态 - 清空选择
        document.getElementById('is-patient').checked = false;
        document.getElementById('not-patient').checked = false;
        this.patientStatus = null;
        
        // 重置情感类型 - 清空选择
        document.getElementById('neutral-type').checked = false;
        document.getElementById('non-neutral-type').checked = false;
        this.emotionType = null;
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

