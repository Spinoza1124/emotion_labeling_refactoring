// 一致性测试相关变量
let consistencyQuestions = [];
let currentQuestionIndex = 0;
let userAnswers = [];
let username = '';

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeSliders();
    checkUrlUsername();
});

// 检查URL参数中的用户名
function checkUrlUsername() {
    const urlParams = new URLSearchParams(window.location.search);
    const urlUsername = urlParams.get('username');
    
    if (urlUsername) {
        // 如果URL中有用户名，直接使用并开始测试
        username = urlUsername;
        document.getElementById('usernameInput').value = username;
        
        // 直接跳过用户名输入，开始测试
        document.getElementById('usernameSection').classList.add('hidden');
        document.getElementById('testSection').classList.remove('hidden');
        
        // 加载测试题目
        loadConsistencyQuestions();
    }
}

// 初始化滑块
function initializeSliders() {
    const vSlider = document.getElementById('vSlider');
    const aSlider = document.getElementById('aSlider');
    const vValue = document.getElementById('vValue');
    const aValue = document.getElementById('aValue');
    
    vSlider.addEventListener('input', function() {
        vValue.textContent = this.value;
    });
    
    aSlider.addEventListener('input', function() {
        aValue.textContent = this.value;
    });
}

// 开始一致性测试
function startConsistencyTest() {
    const usernameInput = document.getElementById('usernameInput');
    username = usernameInput.value.trim();
    
    if (!username) {
        alert('请输入用户名');
        return;
    }
    
    // 隐藏用户名输入区域，显示测试区域
    document.getElementById('usernameSection').classList.add('hidden');
    document.getElementById('testSection').classList.remove('hidden');
    
    // 加载测试题目
    loadConsistencyQuestions();
}

// 加载一致性测试题目
function loadConsistencyQuestions() {
    fetch('/api/consistency/questions')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                consistencyQuestions = data.questions;
                userAnswers = new Array(consistencyQuestions.length);
                
                if (consistencyQuestions.length > 0) {
                    showQuestion(0);
                } else {
                    alert('没有找到一致性测试题目');
                }
            } else {
                alert('加载测试题目失败: ' + data.error);
            }
        })
        .catch(error => {
            console.error('加载测试题目失败:', error);
            alert('加载测试题目失败，请检查网络连接');
        });
}

// 显示指定题目
function showQuestion(index) {
    if (index < 0 || index >= consistencyQuestions.length) {
        return;
    }
    
    currentQuestionIndex = index;
    const question = consistencyQuestions[index];
    
    // 更新进度
    updateProgress();
    
    // 更新题目信息
    const questionElement = document.getElementById('consistencyQuestion');
    questionElement.innerHTML = `
        <strong>音频文件:</strong> ${question.filename}<br>
        <small>请听音频并进行情感标注</small>
    `;
    
    // 加载音频
    const audioPlayer = document.getElementById('audioPlayer');
    audioPlayer.src = `/api/consistency/audio/${question.filename}`;
    
    // 恢复之前的答案（如果有）
    if (userAnswers[index]) {
        restoreAnswer(userAnswers[index]);
    } else {
        resetForm();
    }
    
    // 更新按钮状态
    updateNavigationButtons();
}

// 更新进度条
function updateProgress() {
    const progressText = document.getElementById('progressText');
    const progressBar = document.getElementById('progressBar');
    
    const current = currentQuestionIndex + 1;
    const total = consistencyQuestions.length;
    const percentage = (current / total) * 100;
    
    progressText.textContent = `题目 ${current} / ${total}`;
    progressBar.style.width = `${percentage}%`;
}

// 重置表单
function resetForm() {
    document.getElementById('vSlider').value = 0;
    document.getElementById('aSlider').value = 3;
    document.getElementById('vValue').textContent = '0';
    document.getElementById('aValue').textContent = '3';
    
    // 重置单选按钮
    document.getElementById('nonNeutral').checked = true;
    document.getElementById('patient').checked = true;
    
    // 清除离散情感选择
    const discreteRadios = document.querySelectorAll('input[name="discreteEmotion"]');
    discreteRadios.forEach(radio => radio.checked = false);
}

// 恢复之前的答案
function restoreAnswer(answer) {
    document.getElementById('vSlider').value = answer.v_value || 0;
    document.getElementById('aSlider').value = answer.a_value || 3;
    document.getElementById('vValue').textContent = answer.v_value || '0';
    document.getElementById('aValue').textContent = answer.a_value || '3';
    
    // 恢复情感类型
    if (answer.emotion_type) {
        const emotionTypeRadio = document.querySelector(`input[name="emotionType"][value="${answer.emotion_type}"]`);
        if (emotionTypeRadio) emotionTypeRadio.checked = true;
    }
    
    // 恢复离散情感
    if (answer.discrete_emotion) {
        const discreteEmotionRadio = document.querySelector(`input[name="discreteEmotion"][value="${answer.discrete_emotion}"]`);
        if (discreteEmotionRadio) discreteEmotionRadio.checked = true;
    }
    
    // 恢复患者状态
    if (answer.patient_status) {
        const patientStatusRadio = document.querySelector(`input[name="patientStatus"][value="${answer.patient_status}"]`);
        if (patientStatusRadio) patientStatusRadio.checked = true;
    }
}

// 保存当前答案
function saveCurrentAnswer() {
    const vValue = parseFloat(document.getElementById('vSlider').value);
    const aValue = parseFloat(document.getElementById('aSlider').value);
    const emotionType = document.querySelector('input[name="emotionType"]:checked')?.value;
    const discreteEmotion = document.querySelector('input[name="discreteEmotion"]:checked')?.value;
    const patientStatus = document.querySelector('input[name="patientStatus"]:checked')?.value;
    
    userAnswers[currentQuestionIndex] = {
        filename: consistencyQuestions[currentQuestionIndex].filename,
        v_value: vValue,
        a_value: aValue,
        emotion_type: emotionType,
        discrete_emotion: discreteEmotion,
        patient_status: patientStatus
    };
}

// 上一题
function previousQuestion() {
    if (currentQuestionIndex > 0) {
        saveCurrentAnswer();
        showQuestion(currentQuestionIndex - 1);
    }
}

// 下一题
function nextQuestion() {
    // 验证当前题目是否已完成
    if (!validateCurrentAnswer()) {
        alert('请完成当前题目的所有标注');
        return;
    }
    
    saveCurrentAnswer();
    
    if (currentQuestionIndex < consistencyQuestions.length - 1) {
        showQuestion(currentQuestionIndex + 1);
    }
}

// 验证当前答案
function validateCurrentAnswer() {
    const emotionType = document.querySelector('input[name="emotionType"]:checked');
    const discreteEmotion = document.querySelector('input[name="discreteEmotion"]:checked');
    const patientStatus = document.querySelector('input[name="patientStatus"]:checked');
    
    return emotionType && discreteEmotion && patientStatus;
}

// 更新导航按钮
function updateNavigationButtons() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    
    // 上一题按钮
    prevBtn.disabled = currentQuestionIndex === 0;
    
    // 下一题和提交按钮
    if (currentQuestionIndex === consistencyQuestions.length - 1) {
        nextBtn.classList.add('hidden');
        submitBtn.classList.remove('hidden');
    } else {
        nextBtn.classList.remove('hidden');
        submitBtn.classList.add('hidden');
    }
}

// 提交一致性测试
function submitConsistencyTest() {
    // 验证最后一题
    if (!validateCurrentAnswer()) {
        alert('请完成当前题目的所有标注');
        return;
    }
    
    saveCurrentAnswer();
    
    // 检查是否所有题目都已完成
    const incompleteQuestions = [];
    for (let i = 0; i < userAnswers.length; i++) {
        if (!userAnswers[i] || !userAnswers[i].emotion_type || !userAnswers[i].discrete_emotion || !userAnswers[i].patient_status) {
            incompleteQuestions.push(i + 1);
        }
    }
    
    if (incompleteQuestions.length > 0) {
        alert(`以下题目尚未完成: ${incompleteQuestions.join(', ')}`);
        return;
    }
    
    // 提交结果
    const submitData = {
        username: username,
        results: userAnswers
    };
    
    fetch('/api/consistency/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(submitData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 更新用户的一致性测试跳过设置
            updateUserTestSettings(username, true, true)
                .then(() => {
                    // 显示完成页面
                    document.getElementById('testSection').classList.add('hidden');
                    document.getElementById('completionSection').classList.remove('hidden');
                })
                .catch(error => {
                    console.error('更新用户测试设置失败:', error);
                    // 即使更新失败，也显示完成页面
                    document.getElementById('testSection').classList.add('hidden');
                    document.getElementById('completionSection').classList.remove('hidden');
                });
        } else {
            alert('提交失败: ' + data.error);
        }
    })
    .catch(error => {
        console.error('提交失败:', error);
        alert('提交失败，请检查网络连接');
    });
}

// 跳转到指定题目
function goToQuestion(index) {
    if (index >= 0 && index < consistencyQuestions.length) {
        saveCurrentAnswer();
        showQuestion(index);
    }
}

/**
 * 更新用户测试设置
 * @param {string} username - 用户名
 * @param {boolean} skipTest - 是否跳过测试
 * @param {boolean} skipConsistencyTest - 是否跳过一致性测试
 * @returns {Promise} 更新结果
 */
async function updateUserTestSettings(username, skipTest, skipConsistencyTest) {
    try {
        const response = await fetch('/admin/api/users/test-settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                skip_test: skipTest,
                skip_consistency_test: skipConsistencyTest
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || '更新用户测试设置失败');
        }
        
        return data;
    } catch (error) {
        console.error('更新用户测试设置时发生错误:', error);
        throw error;
    }
}