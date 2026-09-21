<template>
  <div class="home-container">
    <header class="hero-section">
      <button type="button" class="hero-guide-link" @click="router.push({ name: 'Guide' })">使用说明</button>
      <h1>智能写作助手</h1>
      <p>你的全流程 AI 写作伴侣</p>
      <div class="identity-picker" role="group" aria-label="选择身份">
        <span>当前身份</span>
        <button
          type="button"
          :class="{ active: educationLevel === 'high_school' }"
          @click="setEducationLevel('high_school')"
        >高中</button>
        <button
          type="button"
          :class="{ active: educationLevel === 'university' }"
          @click="setEducationLevel('university')"
        >大学</button>
      </div>
      <button @click="createNewDocument" class="create-btn">✨ 开始新的创作</button>
    </header>

    <main class="history-section">
      <div class="history-heading">
        <h2>📜 历史记录</h2>
      </div>
      <div v-if="isLoading" class="loading-text">
        <div class="spinner"></div>
        <p>正在加载中...</p>
      </div>

      <div v-else-if="loadError" class="empty-state load-error-state">
        <p>历史记录暂时无法加载</p>
        <button class="retry-btn" @click="fetchDocuments">重新加载</button>
      </div>
      
      <div v-else-if="documents.length === 0" class="empty-state">
        暂无写作记录，快去创建一个吧！
      </div>
      
      <div v-else class="card-grid">
        <div v-for="doc in documents" :key="doc.id" class="doc-card" @click="openDocument(doc.id)">
          <div class="card-header">
            <h3 :title="doc.topic">{{ summarizeTopic(doc.topic) }}</h3>
            <span class="tag" :class="{ 'scored': doc.score_report }">
              {{ doc.score_report ? '已评分' : '草稿' }}
            </span>
          </div>
          <div class="card-body">
            <p class="preview-text">{{ stripHtml(doc.user_text) }}</p>
          </div>
          <div class="card-footer">
            <span class="edit-time">{{ formatTime(doc) }}</span>
            <div class="actions">
              <button class="delete-btn" @click.stop="deleteDocument(doc.id)" title="删除">🗑️</button>
              <button class="open-btn">继续写作</button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <div v-if="deleteTarget" class="modal-backdrop" @click.self="cancelDelete">
      <section class="confirm-modal" role="dialog" aria-modal="true" aria-labelledby="delete-title">
        <div class="modal-icon">?</div>
        <h2 id="delete-title">删除这篇文章？</h2>
        <p>删除后将无法恢复{{ deleteTarget.topic ? `：“${summarizeTopic(deleteTarget.topic)}”` : '' }}。</p>
        <div class="modal-actions">
          <button type="button" class="modal-btn modal-btn-cancel" @click="cancelDelete">暂不删除</button>
          <button type="button" class="modal-btn modal-btn-danger" @click="confirmDelete">确认删除</button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const router = useRouter();
const documents = ref([]);
const isLoading = ref(true);
const loadError = ref(false);
const deleteTarget = ref(null);
const educationLevel = ref(localStorage.getItem('educationLevel') || 'high_school');

function setEducationLevel(level) {
  educationLevel.value = level;
  localStorage.setItem('educationLevel', level);
}

// 获取列表函数
async function fetchDocuments() {
  isLoading.value = true;
  loadError.value = false;

  try {
    const response = await axios.get(`${API_BASE_URL}/documents?t=${new Date().getTime()}`, {
      timeout: 8000,
    });
    documents.value = response.data;
  } catch (error) {
    console.error('历史记录加载失败:', error);
    loadError.value = true;
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchDocuments();
});

function createNewDocument() {
  router.push({ name: 'Create', query: { educationLevel: educationLevel.value } });
}

function openDocument(id) {
  router.push({ name: 'Editor', params: { id: id } });
}

// 去除HTML标签，提取纯文本
function stripHtml(html) {
  if (!html) return "暂无内容...";
  // 移除所有HTML标签
  const text = decodeHtmlEntities(html.replace(/<[^>]*>/g, '')).trim();
  // 限制长度，两行约80字符
  return text.length > 80 ? text.substring(0, 80) + '...' : text;
}

function summarizeTopic(topic) {
  const normalized = decodeHtmlEntities(topic || '').replace(/\s+/g, ' ').trim();
  if (!normalized) return '未命名主题';

  const firstSentence = normalized.split(/[。！？!?；;\n]/)[0].trim();
  const summary = firstSentence || normalized;
  return summary.length > 48 ? `${summary.substring(0, 48).trim()}...` : summary;
}

function decodeHtmlEntities(value) {
  const decoder = document.createElement('textarea');
  decoder.innerHTML = value;
  return decoder.value;
}

// 友好时间显示
function formatTime(doc) {
  // 优先使用 updated_at，没有则用 created_at
  const timeStr = doc.updated_at || doc.created_at;
  if (!timeStr) return '';
  
  const date = parseApiTime(timeStr);
  if (Number.isNaN(date.getTime())) return '';
  const now = new Date();
  const diff = now - date; // 毫秒差
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 30) return `${days}天前`;
  
  // 超过30天显示具体日期
  return `${date.getMonth() + 1}月${date.getDate()}日`;
}

function parseApiTime(timeStr) {
  const value = String(timeStr).trim();
  // SQLite CURRENT_TIMESTAMP returns UTC without a timezone suffix.
  if (!/[zZ]|[+-]\d{2}:?\d{2}$/.test(value)) {
    return new Date(`${value}Z`);
  }
  return new Date(value);
}

function deleteDocument(id) {
  deleteTarget.value = documents.value.find((doc) => doc.id === id) || { id };
}

function cancelDelete() {
  deleteTarget.value = null;
}

async function confirmDelete() {
  const target = deleteTarget.value;
  if (!target) return;

  try {
    await axios.delete(`${API_BASE_URL}/documents/${target.id}`);
    documents.value = documents.value.filter(d => d.id !== target.id);
    deleteTarget.value = null;
  } catch (error) {
    console.error("删除失败:", error);
  }
}
</script>

<style scoped>
.home-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 48px 40px;
}

.hero-section {
  position: relative;
  text-align: center;
  padding: 72px 56px;
  background: linear-gradient(135deg, 
    rgba(99, 102, 241, 0.95) 0%, 
    rgba(79, 70, 229, 0.92) 40%, 
    rgba(67, 56, 202, 0.95) 100%);
  color: white;
  border-radius: 20px;
  margin-bottom: 40px;
  box-shadow: 
    0 4px 6px rgba(79, 70, 229, 0.1),
    0 20px 50px rgba(79, 70, 229, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  overflow: hidden;
}
.hero-guide-link { position: absolute; top: 20px; right: 24px; z-index: 2; padding: 8px 14px; border: 1px solid rgba(255,255,255,.45); border-radius: 8px; background: rgba(255,255,255,.16); color: #fff; cursor: pointer; font-weight: 600; }
.hero-guide-link:hover { background: rgba(255,255,255,.28); }

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.1) 0%, transparent 50%);
  pointer-events: none;
}

.hero-section h1 {
  margin: 0 0 12px;
  font-size: 3em;
  font-weight: 800;
  letter-spacing: 2px;
  text-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.hero-section p {
  margin: 0;
  opacity: 0.92;
  letter-spacing: 1px;
  font-size: 1.1em;
  font-weight: 400;
}

.identity-picker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 22px;
  padding: 6px;
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: 10px;
  font-size: 14px;
}
.identity-picker button {
  padding: 6px 14px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: white;
  cursor: pointer;
}
.identity-picker button.active { background: white; color: #4338ca; font-weight: 600; }

.create-btn {
  margin-top: 32px;
  padding: 16px 120px;
  font-size: 1em;
  border: none;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.95);
  color: #4338ca;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 700;
  letter-spacing: 0.5px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.create-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
  background: #fff;
}

.history-section h2 {
  border: none;
  padding-bottom: 16px;
  margin-bottom: 24px;
  color: #1f2937;
  font-size: 1.25em;
  font-weight: 700;
  letter-spacing: 0.3px;
}
.history-heading { display: flex; align-items: center; justify-content: space-between; gap: 16px; }

.loading-text {
  text-align: center;
  color: #6b7280;
  margin-top: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 64px 32px;
  color: #9ca3af;
  background: #fff;
  border-radius: 16px;
  border: 1px solid #f0f0f0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  font-size: 0.95em;
}

.load-error-state p { margin: 0 0 16px; }
.retry-btn {
  padding: 9px 18px;
  border: 0;
  border-radius: 8px;
  background: #6366f1;
  color: white;
  cursor: pointer;
}
.retry-btn:hover { background: #4f46e5; }

.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(31, 41, 55, 0.38);
}
.confirm-modal {
  width: min(420px, 100%);
  padding: 28px;
  border: 1px solid #f1f5f9;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.2);
  text-align: center;
}
.modal-icon {
  width: 36px;
  height: 36px;
  margin: 0 auto 14px;
  border-radius: 50%;
  background: #fff1f2;
  color: #e11d48;
  font-size: 22px;
  font-weight: 700;
  line-height: 36px;
}
.confirm-modal h2 { margin: 0 0 10px; color: #1f2937; font-size: 20px; }
.confirm-modal p { margin: 0; color: #6b7280; line-height: 1.7; word-break: break-word; }
.modal-actions { display: flex; justify-content: center; gap: 10px; margin-top: 24px; }
.modal-btn { padding: 10px 18px; border: 0; border-radius: 8px; cursor: pointer; font-size: 14px; }
.modal-btn-cancel { background: #f3f4f6; color: #4b5563; }
.modal-btn-cancel:hover { background: #e5e7eb; }
.modal-btn-danger { background: #e11d48; color: #fff; }
.modal-btn-danger:hover { background: #be123c; }

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 24px;
}

.doc-card {
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), 0 8px 24px rgba(0, 0, 0, 0.02);
}

.doc-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06), 0 16px 40px rgba(0, 0, 0, 0.06);
  transform: translateY(-4px);
  border-color: #e5e7eb;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14px;
  gap: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 1.1em;
  color: #111827;
  font-weight: 700;
  letter-spacing: 0.2px;
  line-height: 1.4;
  flex: 1;
}

.tag {
  background: #f5f3ff;
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 0.75em;
  color: #6366f1;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}

.tag.scored {
  background: #ecfdf5;
  color: #059669;
}

.preview-text {
  color: #4b5563;
  font-size: 0.9em;
  height: 44px;
  overflow: hidden;
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  text-overflow: ellipsis;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid #f5f5f5;
}

.edit-time {
  font-size: 0.8em;
  color: #9ca3af;
  letter-spacing: 0.2px;
}

.actions {
  display: flex;
  gap: 16px;
  align-items: center;
}

.delete-btn {
  background: none;
  border: none;
  color: #d1d5db;
  cursor: pointer;
  font-size: 1em;
  padding: 6px;
  border-radius: 8px;
  transition: all 0.2s;
  line-height: 1;
}

.delete-btn:hover {
  background: #fef2f2;
  color: #ef4444;
}

.open-btn {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none;
  color: #fff;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85em;
  padding: 8px 18px;
  border-radius: 8px;
  letter-spacing: 0.3px;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
}

.open-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
}
</style>
