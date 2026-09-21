<template>
  <div class="create-container">
    <!-- 返回按钮 - 精致图标样式 -->
    <nav class="nav-bar">
      <button @click="$router.push('/')" class="back-btn" title="返回首页">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
      </button>
    </nav>

    <!-- 主 Banner - 弥散光效果 -->
    <header class="hero-section">
      <div class="mesh-gradient"></div>
      <div class="hero-content">
        <h1>开启新的创作旅程</h1>
        <p>输入你的写作主题，AI 将为你生成大纲和灵感</p>
      </div>
    </header>

    <!-- 核心输入区 -->
    <main class="input-section">
      <div class="input-wrapper">
        <div class="selection-row">
          <label>
            <span>写作者身份</span>
            <select v-model="educationLevel" class="select-input">
              <option value="high_school">高中</option>
              <option value="university">大学</option>
            </select>
          </label>
          <label>
            <span>作文语言</span>
            <select v-model="language" class="select-input">
              <option value="zh">中文议论文</option>
              <option value="en">英文议论文</option>
            </select>
          </label>
        </div>
        <input 
          v-model="topic" 
          type="text" 
          placeholder="例如：论人工智能对未来教育的影响..." 
          class="topic-input"
          @keyup.enter="handleCreate"
          autofocus
        />
      </div>

      <div class="actions">
        <button 
          @click="handleCreate" 
          class="start-btn"
          :disabled="!topic.trim() || isCreating"
        >
          <span v-if="isCreating">正在准备中...</span>
          <span v-else>✨ 开始写作</span>
        </button>
      </div>

      <!-- 提示卡片 -->
      <div class="tips-card">
        <h3>写作小贴士</h3>
        <ul class="tips-list">
          <li>
            <span class="tip-icon">🎯</span>
            <span class="tip-text">主题越具体，生成的大纲越精准</span>
          </li>
          <li>
            <span class="tip-icon">📝</span>
            <span class="tip-text">请输入一个议论文题目，或简单描述你想讨论的主题</span>
          </li>
          <li>
            <span class="tip-icon">💡</span>
            <span class="tip-text">创建后会先准备基础大纲；需要更多帮助时，可在写作页主动获取结构或举例提示</span>
          </li>
        </ul>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const router = useRouter();
const topic = ref('');
const isCreating = ref(false);
const educationLevel = ref(router.currentRoute.value.query.educationLevel || localStorage.getItem('educationLevel') || 'high_school');
const language = ref('zh');

async function handleCreate() {
  if (!topic.value.trim()) return;
  
  isCreating.value = true;
  try {
    // 增加超时设置，防止请求无限挂起
    const response = await axios.post(`${API_BASE_URL}/documents`, {
      topic: topic.value,
      education_level: educationLevel.value,
      language: language.value,
    }, { timeout: 60000 }); // 60秒超时
    
    // 创建成功后跳转到编辑器
    router.push({ name: 'Editor', params: { id: response.data.id } });
  } catch (error) {
    console.error("创建失败:", error);
    let msg = "创建失败，请检查后端服务";
    if (error.code === 'ECONNABORTED') {
      msg = "请求超时，后端响应过慢";
    } else if (error.response) {
      msg = `服务器错误: ${error.response.status}`;
    }
    alert(msg);
  } finally {
    isCreating.value = false;
  }
}
</script>

<style scoped>
.create-container {
  min-height: 100vh;
  background: #F8FAFC;
  padding: 32px 40px;
  font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* 返回按钮 - 精致图标样式 */
.nav-bar { 
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  box-sizing: border-box;
  margin: 0 0 24px;
  padding: 0 0;
}

.back-btn {
  position: relative;
  background: #fff;
  color: #6b7280;
  border: 1px solid #e5e7eb;
  width: 52px;
  height: 52px;
  padding: 0;
  margin: 0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.back-btn svg {
  position: absolute;
  top: 50%;
  left: 50%;
  display: block;
  width: 26px;
  height: 26px;
  transform: translate(-50%, -50%);
  fill: none;
  stroke: currentColor;
  stroke-width: 2.5;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.back-btn:hover { 
  background: #fff;
  color: #4f46e5;
  border-color: #c7d2fe;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15);
  transform: translateY(-1px);
}

/* 主 Banner - 弥散光效果 */
.hero-section {
  position: relative;
  text-align: center;
  padding: 72px 48px;
  background: linear-gradient(135deg, #5b21b6 0%, #6d28d9 30%, #7c3aed 60%, #8b5cf6 100%);
  color: white;
  border-radius: 16px;
  margin: 0 auto 48px;
  max-width: 1000px;
  overflow: hidden;
}

/* 弥散光背景 */
.mesh-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(ellipse 80% 50% at 20% 40%, rgba(167, 139, 250, 0.4) 0%, transparent 50%),
    radial-gradient(ellipse 60% 80% at 80% 20%, rgba(139, 92, 246, 0.3) 0%, transparent 50%),
    radial-gradient(ellipse 50% 60% at 60% 80%, rgba(192, 132, 252, 0.35) 0%, transparent 50%),
    radial-gradient(ellipse 40% 40% at 30% 70%, rgba(124, 58, 237, 0.25) 0%, transparent 50%);
  pointer-events: none;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-section h1 { 
  margin: 0; 
  font-size: 2.75em; 
  font-weight: 800;
  letter-spacing: 1px;
  text-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.hero-section p { 
  margin-top: 14px; 
  font-size: 1.1em; 
  opacity: 0.9;
  letter-spacing: 0.5px;
  font-weight: 400;
}

/* 核心输入区 */
.input-section {
  max-width: 720px;
  margin: 0 auto;
  text-align: center;
}

.input-wrapper {
  margin-bottom: 32px;
}

.selection-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 18px;
  text-align: left;
}
.selection-row label { display: grid; gap: 7px; color: #475569; font-size: 14px; font-weight: 600; }
.select-input { padding: 12px 14px; border: 1px solid #e2e8f0; border-radius: 10px; background: white; color: #1e293b; font-size: 15px; }

.topic-input {
  width: 100%;
  padding: 22px 28px;
  font-size: 17px;
  border: 1.5px solid #e2e8f0;
  border-radius: 14px;
  outline: none;
  transition: all 0.25s ease;
  box-sizing: border-box;
  background: #fff;
  color: #1e293b;
  letter-spacing: 0.3px;
}

.topic-input::placeholder {
  color: #cbd5e1;
  font-weight: 400;
}

.topic-input:focus {
  border-color: #8b5cf6;
  box-shadow: 
    0 0 0 4px rgba(139, 92, 246, 0.12),
    0 4px 20px rgba(139, 92, 246, 0.1);
}

/* 开始按钮 */
.actions {
  margin-bottom: 56px;
}

.start-btn {
  background: #5b21b6;
  color: white;
  border: none;
  padding: 18px 100px;
  font-size: 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s ease;
  font-weight: 600;
  letter-spacing: 0.5px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  box-shadow: 0 4px 14px rgba(91, 33, 182, 0.25);
}

.start-btn:hover:not(:disabled) {
  background: #4c1d95;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(91, 33, 182, 0.35);
}

.start-btn:active:not(:disabled) {
  transform: translateY(0);
}

.start-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}

/* 提示卡片 */
.tips-card {
  background: #f1f5f9;
  padding: 28px 32px;
  border-radius: 14px;
  text-align: left;
  border: 1px solid #e2e8f0;
}

.tips-card h3 {
  margin: 0 0 20px;
  color: #475569;
  font-size: 0.95em;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.tips-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.tips-list li {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 0;
  border-bottom: 1px solid #e2e8f0;
}

.tips-list li:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.tips-list li:first-child {
  padding-top: 0;
}

.tip-icon {
  font-size: 1.1em;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.tip-text {
  color: #64748b;
  font-size: 0.9em;
  line-height: 1.6;
  letter-spacing: 0.2px;
}
</style>