<template>
  <nav class="editor-nav">
  <button @click="$router.push('/')" class="back-btn">返回首页</button>
  <span class="doc-title">{{ document?.topic }}</span>
  </nav>
  <div class="app-bg">
    <div class="editor-container">
      <!-- 加载状态 -->
      <div v-if="!document" class="loading-state">
        <div class="spinner"></div>
        <p>正在加载文档...</p>
      </div>

      <!-- 主内容区 -->
      <div v-else class="content-wrapper">
        <!-- 顶部导航/标题栏 -->
        <header class="header-section">
          <div class="header-left">
            <span class="topic-label">正在写作</span>
            <h1 class="topic-title">{{ document.topic }}</h1>
            <span class="mode-label">{{ isChinese ? '中文议论文' : '英文议论文' }} · {{ document.education_level === 'high_school' ? '高中' : '大学' }}</span>
          </div>
          <div class="save-status">
            <span class="status-dot" :class="{ 'saving': isSaving, 'saved': !isSaving }"></span>
            {{ saveStatusText }}
          </div>
        </header>
        
        
        <div :class="['main-layout', { 'is-completed': isCompleted }]">
          <!-- 左侧：写作核心区 -->
          <div class="writing-column">
            <div v-if="isChinese" class="title-field">
              <label for="essay-title">文章标题</label>
              <input id="essay-title" v-model="document.title" placeholder="请输入议论文标题" @input="scheduleSave" />
            </div>
            <div class="paper-wrapper">
              <Editor
                v-model="document.user_text"
                tinymce-script-src="/tinymce/tinymce.min.js"
                license-key="gpl"
                :init="tinymceInit"
                @onKeyUp="handleInput"
              />
            </div>
            <div class="action-bar">
              <button v-if="!isChinese && !isCompleted" @click="requestAnalysis('grammar_check')" :disabled="isAnalyzing" :class="['btn', 'btn-secondary', { 'is-busy': activeAnalysisAction === 'grammar_check' }]">
                {{ analysisButtonText('grammar_check') }}
              </button>
              <button v-if="!isCompleted" @click="requestAnalysis('outline_hint', true)" :disabled="isAnalyzing" :class="['btn', 'btn-secondary', { 'is-busy': activeAnalysisAction === 'outline_hint' }]">
                {{ analysisButtonText('outline_hint') }}
              </button>
              <button v-if="isChinese && !isCompleted" @click="requestAnalysis('example_hint', true)" :disabled="isAnalyzing" :class="['btn', 'btn-secondary', { 'is-busy': activeAnalysisAction === 'example_hint' }]">
                {{ analysisButtonText('example_hint') }}
              </button>
              <button @click="submitForScoring" :disabled="isScoring || isCompleted" :class="['btn', isCompleted ? 'btn-completed' : 'btn-primary', { 'is-busy': isScoring }]">
                <span v-if="isCompleted">已完成</span>
                <span v-else-if="isScoring">AI 评分中...</span>
                <span v-else>✨ 完成写作，提交评分</span>
              </button>
            </div>

            <div v-if="isCompleted" class="completed-analysis-actions">
              <button v-for="action in completionActions" :key="action.key" @click="requestAnalysis(action.key)" :disabled="isAnalyzing" :class="['analysis-button', { 'is-busy': activeAnalysisAction === action.key }]">
                {{ analysisButtonText(action.key) }}
              </button>
            </div>

            <div v-if="analysisResults.length" class="analysis-report">
              <div v-for="(result, index) in analysisResults" :key="index" class="analysis-item">
                <strong>{{ result.original || '分析结果' }}</strong>
                <p>{{ result.suggestion }}</p>
                <small v-if="result.reason">{{ result.reason }}</small>
              </div>
            </div>

            <!-- 评分报告 (优化版) -->
            <div v-if="scoreReport" class="score-report fade-in">
              <div class="report-header">
                <div class="score-circle">
                  <span class="score-val">{{ scoreReport.overall_score }}</span>
                  <span class="score-max">/10</span>
                </div>
                <div class="report-title">
                  <h2>AI 评分报告</h2>
                  <p>生成时间: {{ new Date().toLocaleTimeString() }}</p>
                </div>
              </div>
              
              <!-- 维度卡片网格 -->
              <div class="dimensions-grid">
                <div v-for="(detail, dimension) in scoreReport.dimensions" :key="dimension" class="dimension-card">
                  <div class="dim-header">
                    <h4>{{ dimension }}</h4>
                    <span class="dim-score">{{ detail.score }}分</span>
                  </div>
                  <div class="progress-bg">
                    <div class="progress-fill" :style="{ width: (detail.score * 10) + '%' }"></div>
                  </div>
                  <p class="feedback-text">{{ detail.feedback }}</p>
                </div>
              </div>

              <div class="suggestions-box">
                <h3>💡 改进建议</h3>
                <ul>
                  <li v-for="(suggestion, index) in scoreReport.suggestions" :key="index">{{ suggestion }}</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- 右侧：侧边栏 (固定悬浮) -->
          <div v-if="!isCompleted" class="sidebar-column">
            <div class="sticky-wrapper">
              <div v-if="showOutlinePanel && !isCompleted" class="sidebar-card outline-card">
                <div class="card-header">
                  <h3>📋 写作大纲</h3>
                </div>
                  <div class="card-body scrollable-content">
                  <div v-if="generatedOutline.length" class="outline-list">
                    <div v-for="(item, index) in generatedOutline" :key="index" class="outline-item">
                      <span class="index-badge">{{ index + 1 }}</span>
                      <div>
                        <p>{{ item.title }}</p>
                        <small v-if="item.content">{{ item.content }}</small>
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-raw">
                    暂无大纲提示
                  </div>
                </div>
              </div>

              <div v-if="showMaterialsPanel && !isCompleted && isChinese && generatedMaterials.length" class="sidebar-card materials-card">
                <div class="card-header">
                  <h3>💡 举例提示</h3>
                </div>
                 <div class="card-body material-list">
                   <div v-for="(mat, idx) in generatedMaterials" :key="idx" class="material-item">
                     <span class="material-tag">{{ mat.type }}</span>
                     <p class="material-content">{{ mat.content }}</p>
                   </div>
                 </div>
              </div>
              
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-if="showAnalysisConfirm" class="modal-backdrop" @click.self="cancelAnalysis">
    <section class="confirm-modal" role="dialog" aria-modal="true" aria-labelledby="confirm-title">
      <h2 id="confirm-title">需要一点提示吗？</h2>
      <p>建议先独立思考，再使用 AI 提示。确定要继续吗？</p>
      <div class="modal-actions">
        <button type="button" class="modal-btn modal-btn-cancel" @click="cancelAnalysis">暂不需要</button>
        <button type="button" class="modal-btn modal-btn-confirm" @click="confirmAnalysis">继续获取</button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import Editor from '@tinymce/tinymce-vue'; // 导入 TinyMCE Vue 组件

// 自定义防抖函数，避免依赖 lodash
const props = defineProps({ id: String });

// TinyMCE 编辑器配置
const tinymceInit = {
  license_key: 'gpl', // 官方文档推荐
  licenseKey: 'gpl', // 尝试兼容写法
  base_url: '/tinymce', // 指向 public/tinymce 目录
  language: 'zh_CN', // 中文界面
  language_url: '/tinymce/langs/zh_CN.js', // 中文语言包路径
  height: 600,
  menubar: false,
  branding: false, // 隐藏 TinyMCE 品牌
  promotion: false, // 隐藏升级提示
  plugins: [
    'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
    'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
    'insertdatetime', 'media', 'table', 'wordcount', 'autosave'
  ],
  toolbar: 'undo redo | bold italic underline',
  elementpath: false,
  statusbar: true,
  content_style: `
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      font-size: 16px;
      line-height: 1.8;
      color: #333;
      padding: 20px;
    }
    p { margin: 0 0 1em 0; }
    .ai-error-underline {
      text-decoration: underline wavy #ff4d4f;
      text-underline-offset: 3px;
      background-color: rgba(255, 77, 79, 0.1);
      cursor: help;
    }
  `,
  placeholder: '在此处开始您的写作...',
  autosave_interval: '30s',
  autosave_prefix: 'writing-assistant-{path}{query}-',
  autosave_restore_when_empty: false,
};

const document = ref(null);
const scoreReport = ref(null);
const isSaving = ref(false);
const isScoring = ref(false);
const isAnalyzing = ref(false);
const lastSavedTime = ref('');
const analysisResults = ref([]);
const showOutlinePanel = ref(false);
const showMaterialsPanel = ref(false);
const showAnalysisConfirm = ref(false);
const pendingAnalysisAction = ref(null);
const activeAnalysisAction = ref(null);
const generatedOutline = ref([]);
const generatedMaterials = ref([]);

const API_URL = `${API_BASE_URL}/documents`;

const isChinese = computed(() => document.value?.language !== 'en');
const isCompleted = computed(() => Boolean(scoreReport.value));
const completionActions = computed(() => isChinese.value
  ? [
      { key: 'title_optimize', label: '标题优化' },
      { key: 'grammar_check', label: '全文语法检测' },
      { key: 'logic_optimize', label: '整体逻辑优化' },
      { key: 'example_expansion', label: '扩充可用样例' },
      { key: 'style_polish', label: '句式润色' },
    ]
  : [
      { key: 'grammar_check', label: '全文语法检测' },
      { key: 'style_polish', label: '句式润色' },
      { key: 'structure_check', label: '整体结构检查' },
    ]);

const analysisLabels = {
  grammar_check: '检查当前语法',
  outline_hint: '获取纲领提示',
  example_hint: '获取举例提示',
  title_optimize: '标题优化',
  logic_optimize: '整体逻辑优化',
  example_expansion: '扩充可用样例',
  style_polish: '句式润色',
  structure_check: '整体结构检查',
};

function analysisButtonText(action) {
  return activeAnalysisAction.value === action ? `${analysisLabels[action]}进行中...` : analysisLabels[action];
}

const saveStatusText = computed(() => {
  if (isSaving.value) return '正在保存...';
  if (lastSavedTime.value) return `已保存 ${lastSavedTime.value}`;
  return '准备就绪';
});

onMounted(async () => {
  try {
    const response = await axios.get(`${API_URL}/${props.id}`);
    document.value = response.data;
    if (response.data.score_report) {
      scoreReport.value = response.data.score_report;
    }
  } catch (error) {
    console.error("加载文档失败", error);
  }
});

let autoSaveTimer = null;
function handleInput() {
  if (autoSaveTimer) clearTimeout(autoSaveTimer);
  autoSaveTimer = setTimeout(() => {
    saveProgress(true);
  }, 1500);
}

function manualSave() {
  saveProgress(false);
}

function scheduleSave() {
  handleInput();
}

async function saveProgress(isAuto = false) {
  isSaving.value = true;
  try {
    await axios.put(`${API_URL}/${props.id}`, {
      user_text: document.value.user_text,
      title: document.value.title || '',
    });
    const now = new Date();
    lastSavedTime.value = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
  } catch (error) {
    console.error('保存失败:', error);
  } finally {
    isSaving.value = false;
  }
}

async function requestAnalysis(action, requiresConfirmation = false) {
  if (requiresConfirmation) {
    pendingAnalysisAction.value = action;
    showAnalysisConfirm.value = true;
    return;
  }

  await runAnalysis(action);
}

async function confirmAnalysis() {
  const action = pendingAnalysisAction.value;
  cancelAnalysis();
  if (action) await runAnalysis(action);
}

function cancelAnalysis() {
  showAnalysisConfirm.value = false;
  pendingAnalysisAction.value = null;
}

async function runAnalysis(action) {
  isAnalyzing.value = true;
  activeAnalysisAction.value = action;
  try {
    const isPlanningAction = action === 'outline_hint' || action === 'example_hint';
    const analysisText = isPlanningAction
      ? document.value.topic
      : action === 'title_optimize'
      ? JSON.stringify({
          title: (document.value.title || '').trim(),
          body: document.value.user_text || '',
        })
      : document.value.user_text;
    const response = await axios.post(`${API_URL}/${props.id}/analysis`, {
      action,
      text: analysisText,
    }, { timeout: 120000 });
    analysisResults.value = isPlanningAction ? [] : (response.data.items || []);
    if (!isPlanningAction && response.data.summary) {
      analysisResults.value.unshift({ original: '', suggestion: response.data.summary, reason: '' });
    }
    if (action === 'outline_hint') {
      generatedOutline.value = (response.data.items || []).map((item) => ({
        title: item.suggestion || item.original || '写作方向',
        content: item.reason || '',
      }));
      showOutlinePanel.value = true;
      showMaterialsPanel.value = false;
    }
    if (action === 'example_hint') {
      generatedMaterials.value = (response.data.items || []).map((item) => ({
        type: '举例方向',
        content: item.suggestion || item.original || item.reason || '',
      }));
      showMaterialsPanel.value = true;
      showOutlinePanel.value = false;
    }
  } catch (error) {
    alert(error.response?.data?.detail || 'AI 分析暂时不可用，请稍后重试');
  } finally {
    isAnalyzing.value = false;
    activeAnalysisAction.value = null;
  }
}

async function submitForScoring() {
  await saveProgress(true);
  isScoring.value = true;
  try {
    // 增加 120秒 超时设置（与后端匹配）
    const response = await axios.post(`${API_URL}/${props.id}/score`, {}, { timeout: 120000 });
    scoreReport.value = response.data;
    setTimeout(() => {
      document.querySelector('.score-report')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
  } catch (error) {
    console.error('评分失败:', error);
    let msg = '评分服务暂时不可用，请稍后重试';
    if (error.code === 'ECONNABORTED') {
      msg = '评分请求超时，AI 正在繁忙，请稍后再试';
    } else if (error.response && error.response.status === 429) {
      msg = 'AI 服务请求过于频繁，请等待几秒后重试';
    } else if (error.response && error.response.data && error.response.data.detail) {
      msg = `${error.response.data.detail}`;
    }
    alert(msg);
  } finally {
    isScoring.value = false;
  }
}
</script>

<style scoped>
/* --- 基础布局与背景 --- */
.app-bg {
  min-height: 100vh;
  background-color: #f5f7fa; /* 浅灰背景，区分层次 */
  padding-bottom: 50px;
}

.editor-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 20px 30px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: #2c3e50;
}

/* --- 头部区域 --- */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}
.topic-label {
  font-size: 12px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 1px;
  display: block;
  margin-bottom: 4px;
}
.topic-title {
  margin: 0;
  font-size: 24px;
  color: #303133;
  font-weight: 600;
}
.mode-label { display: block; margin-top: 6px; color: #909399; font-size: 12px; }
.title-field { margin-bottom: 16px; }
.title-field label { display: block; margin-bottom: 7px; color: #606266; font-size: 13px; font-weight: 600; }
.title-field input { width: 100%; box-sizing: border-box; padding: 12px 14px; border: 1px solid #dcdfe6; border-radius: 6px; font-size: 16px; }
.save-status {
  font-size: 13px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 8px;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #67c23a;
}
.status-dot.saving { background-color: #e6a23c; animation: pulse 1s infinite; }

/* --- 主布局 Grid --- */
.main-layout {
  display: flex;
  gap: 30px;
  align-items: flex-start;
}
.main-layout.is-completed .writing-column { width: 100%; }

/* --- 左侧：写作区 --- */
.writing-column {
  flex: 1; /* 占据剩余空间 */
  min-width: 0; /* 关键：防止子元素过宽撑破 Flex */
}

/* 仿纸张的编辑器容器 */
.paper-wrapper {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06); /* 柔和阴影 */
  margin-bottom: 20px;
  transition: box-shadow 0.3s;
  overflow: hidden; /* 让 TinyMCE 圆角生效 */
}
.paper-wrapper:focus-within {
  box-shadow: 0 6px 24px rgba(0,0,0,0.09);
}

/* TinyMCE 编辑器样式覆盖 */
.paper-wrapper :deep(.tox-tinymce) {
  border: none !important;
  border-radius: 8px !important;
}
.paper-wrapper :deep(.tox-editor-header) {
  border-bottom: 1px solid #e4e7ed !important;
  box-shadow: none !important;
}
.paper-wrapper :deep(.tox-toolbar__primary) {
  background: #fafbfc !important;
}
.paper-wrapper :deep(.tox-statusbar) {
  border-top: 1px solid #e4e7ed !important;
}

/* 按钮栏 */
.action-bar {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-bottom: 40px;
}
.btn {
  padding: 10px 20px;
  border-radius: 6px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}
.btn-secondary { background: #eef1f6; color: #606266; }
.btn-secondary:hover { background: #dce1e8; }
.btn-primary { background: #409eff; color: white; box-shadow: 0 4px 12px rgba(64,158,255,0.3); }
.btn-primary:hover { background: #66b1ff; transform: translateY(-1px); }
.btn-completed { background: #d8dde5; color: #6b7280; cursor: default; }
.btn:focus, .analysis-button:focus, .modal-btn:focus { outline: none; }
.btn.is-busy, .analysis-button.is-busy { background: #b8d9f8; color: #2f75b5; box-shadow: none; }
.btn:disabled { opacity: 1; cursor: not-allowed; transform: none; }
.analysis-report { margin-bottom: 30px; padding: 18px 20px; background: #fffdf5; border: 1px solid #faecd8; border-radius: 8px; }
.completed-analysis-actions { display: flex; flex-wrap: wrap; gap: 10px; margin: 4px 0 30px; }
.analysis-item { padding: 10px 0; border-bottom: 1px solid #f5ead8; line-height: 1.5; }
.analysis-item:last-child { border-bottom: 0; }
.analysis-item p { margin: 4px 0; color: #606266; }
.analysis-item small { color: #909399; }
.analysis-buttons { display: grid; gap: 8px; }
.analysis-button { padding: 9px 10px; border: 1px solid #dcdfe6; border-radius: 5px; background: #fff; color: #606266; cursor: pointer; text-align: left; transition: background 0.2s, color 0.2s, border-color 0.2s; }
.analysis-button:hover { border-color: #409eff; color: #409eff; }

.modal-backdrop { position: fixed; inset: 0; z-index: 20; display: flex; align-items: center; justify-content: center; padding: 20px; background: rgba(31, 41, 55, 0.38); }
.confirm-modal { width: min(420px, 100%); padding: 28px; border-radius: 14px; background: #fff; box-shadow: 0 18px 55px rgba(15, 23, 42, 0.22); }
.confirm-modal h2 { margin: 0 0 10px; color: #1f2937; font-size: 20px; }
.confirm-modal p { margin: 0; color: #6b7280; line-height: 1.7; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
.modal-btn { padding: 9px 16px; border: 1px solid transparent; border-radius: 7px; cursor: pointer; font-size: 14px; }
.modal-btn-cancel { background: #f3f4f6; color: #4b5563; }
.modal-btn-confirm { background: #409eff; color: #fff; }
.modal-btn-confirm:hover { background: #3185d6; }

/* --- 右侧：侧边栏 --- */
.sidebar-column {
  width: 320px; /* 固定宽度，看起来更整洁 */
  flex-shrink: 0;
}
.sticky-wrapper {
  position: sticky;
  top: 20px; /* 滚动时吸顶 */
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sidebar-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  border: 1px solid #ebeef5;
  overflow: hidden;
}
.card-header {
  background: #fdfdfd;
  padding: 15px 20px;
  border-bottom: 1px solid #f0f2f5;
}
.card-header h3 { margin: 0; font-size: 16px; color: #303133; }
.card-body {
  padding: 15px 20px;
}
/* 侧边栏内容控制 */
.scrollable-content {
  max-height: 520px;
  overflow-y: auto;
}
.outline-item {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
  font-size: 14px;
  color: #555;
}
.index-badge {
  background: #ecf5ff;
  color: #409eff;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  text-align: center;
  line-height: 20px;
  font-size: 12px;
  flex-shrink: 0;
}
.code-block pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  background: #f9fafc;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
  max-height: 250px;
  overflow-y: auto;
  border: 1px solid #eaeefb;
}

/* --- 评分报告 --- */
.score-report {
  background: #fff;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  border-top: 4px solid #409eff;
}
.report-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px dashed #ebeef5;
}
.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #ecf5ff;
  color: #409eff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

/* 实时建议卡片样式 */
.suggestion-card .card-header h3 { color: #e6a23c; } /* 使用警告色突出 */
.suggestion-card .card-body { padding: 0; } /* 让列表贴边 */
.suggestion-item { 
  padding: 12px 15px; 
  border-bottom: 1px solid #f5f7fa; 
  transition: background 0.2s;
}
.suggestion-item:last-child { border-bottom: none; }
.suggestion-item:hover { background: #fdf6ec; }

.suggestion-content {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 14px;
  flex-wrap: wrap;
}
.error-text { 
  color: #f56c6c; 
  text-decoration: line-through; 
  font-weight: 500;
}
.arrow { color: #909399; font-size: 12px; }
.fix-text { 
  color: #67c23a; 
  font-weight: bold; 
  background: #f0f9eb;
  padding: 2px 6px;
  border-radius: 4px;
}
.reason { 
  font-size: 12px; 
  color: #909399; 
  margin: 0; 
  line-height: 1.4;
}


.score-val { font-size: 32px; line-height: 1; }
.score-max { font-size: 12px; opacity: 0.8; }
.report-title h2 { margin: 0 0 5px 0; font-size: 20px; }
.report-title p { margin: 0; color: #999; font-size: 12px; }

.dimensions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* 双列布局，更紧凑 */
  gap: 20px;
  margin-bottom: 25px;
}
.dimension-card {
  background: #f8fbfd;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #f0f4f8;
}
.dim-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
.dim-header h4 { margin: 0; font-size: 15px; font-weight: 600; }
.dim-score { font-weight: bold; color: #409eff; }
.progress-bg {
  height: 6px;
  background: #ebeef5;
  border-radius: 3px;
  margin-bottom: 10px;
  overflow: hidden;
}
.progress-fill { height: 100%; background: #67c23a; border-radius: 3px; }
.feedback-text { font-size: 13px; color: #606266; margin: 0; line-height: 1.5; }

.suggestions-box {
  background: #fffcf0;
  border: 1px solid #faecd8;
  border-radius: 8px;
  padding: 20px;
}
.suggestions-box h3 { margin-top: 0; color: #e6a23c; font-size: 16px; }
.suggestions-box ul { margin: 0; padding-left: 20px; color: #606266; }
.suggestions-box li { margin-bottom: 5px; }

/* 新增：素材列表样式 */
.material-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.material-item {
  background: #f8f9fa;
  border-left: 3px solid #667eea;
  padding: 10px;
  border-radius: 0 4px 4px 0;
}
.material-tag {
  display: inline-block;
  background: #e0e7ff;
  color: #4338ca;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  margin-bottom: 4px;
  font-weight: bold;
}
.material-content {
  margin: 0;
  font-size: 13px;
  color: #4a5568;
  line-height: 1.5;
}

.editor-nav { display: flex; align-items: center; padding: 10px 20px; background: white; border-bottom: 1px solid #eee; margin-bottom: 20px; }
.back-btn { 
  background: #409eff; 
  color: white; 
  border: none; 
  padding: 8px 20px; 
  border-radius: 20px; 
  font-size: 14px; 
  cursor: pointer; 
  transition: background 0.2s;
}
.back-btn:hover { background: #66b1ff; }
.doc-title { margin-left: 20px; font-weight: bold; font-size: 18px; }


/* 动画 */
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
.fade-in { animation: fadeIn 0.5s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.loading-state { height: 400px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #999; }
.spinner { width: 40px; height: 40px; border: 3px solid #f3f3f3; border-top: 3px solid #409eff; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 15px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>