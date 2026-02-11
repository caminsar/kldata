<template>
  <div class="chat-page">
    <div class="chat-header">
      <h2>智能对话</h2>
      <div class="header-actions">
        <el-select v-model="selectedKbId" placeholder="选择知识库（可选）" clearable style="width: 240px">
          <el-option
            v-for="kb in knowledgeBases"
            :key="kb.id"
            :label="kb.name"
            :value="kb.id"
          />
        </el-select>
        <el-button @click="startNewChat" :icon="Plus">新对话</el-button>
      </div>
    </div>

    <div class="chat-body">
      <!-- 会话列表侧栏 -->
      <div class="session-list">
        <div class="session-list-header">历史会话</div>
        <div
          v-for="s in sessions"
          :key="s.session_id"
          class="session-item"
          :class="{ active: s.session_id === sessionId }"
          @click="loadSession(s.session_id)"
        >
          <span class="session-title">{{ s.title }}</span>
          <el-icon class="session-delete" @click.stop="removeSession(s.session_id)"><Delete /></el-icon>
        </div>
        <div v-if="sessions.length === 0" class="session-empty">暂无历史会话</div>
      </div>

      <!-- 对话区 -->
      <div class="chat-area">
        <div class="messages" ref="messagesRef">
          <div v-if="messages.length === 0" class="empty-chat">
            <el-icon :size="48" color="#c0c4cc"><ChatDotRound /></el-icon>
            <p>开始一段新对话</p>
            <p class="hint">选择知识库后可基于文档内容进行问答</p>
          </div>
          <div
            v-for="(msg, i) in messages"
            :key="i"
            class="message"
            :class="msg.role"
          >
            <div class="message-avatar">
              <el-icon v-if="msg.role === 'user'" :size="20"><User /></el-icon>
              <el-icon v-else :size="20"><Monitor /></el-icon>
            </div>
            <div class="message-content">
              <div class="message-text" v-html="renderMarkdown(msg.content)"></div>
              <div v-if="msg.sources && msg.sources.length" class="message-sources">
                <div class="sources-title">参考来源：</div>
                <div v-for="(src, j) in msg.sources" :key="j" class="source-item">
                  <el-tag size="small" type="info">{{ src.source }}</el-tag>
                  <span class="source-score">相关度: {{ (src.score * 100).toFixed(1) }}%</span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="sending" class="message assistant">
            <div class="message-avatar"><el-icon :size="20"><Monitor /></el-icon></div>
            <div class="message-content">
              <div class="typing-indicator"><span></span><span></span><span></span></div>
            </div>
          </div>
        </div>

        <div class="input-area">
          <el-input
            v-model="question"
            type="textarea"
            :rows="2"
            placeholder="输入您的问题... (Enter 发送, Shift+Enter 换行)"
            @keydown="handleKeydown"
            :disabled="sending"
            resize="none"
          />
          <el-button
            type="primary"
            :icon="Promotion"
            @click="send"
            :loading="sending"
            :disabled="!question.trim()"
          >
            发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { Plus, Promotion, Delete, User, Monitor, ChatDotRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import { sendMessage, getChatHistory, getChatSessions, deleteChatSession, getKnowledgeBases } from '../api'

const knowledgeBases = ref([])
const selectedKbId = ref(null)
const sessionId = ref(null)
const sessions = ref([])
const messages = ref([])
const question = ref('')
const sending = ref(false)
const messagesRef = ref(null)

function renderMarkdown(text) {
  return marked.parse(text || '', { breaks: true })
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

async function fetchKnowledgeBases() {
  try {
    const { data } = await getKnowledgeBases()
    knowledgeBases.value = data
  } catch (e) { /* ignore */ }
}

async function fetchSessions() {
  try {
    const { data } = await getChatSessions(selectedKbId.value)
    sessions.value = data
  } catch (e) { /* ignore */ }
}

function startNewChat() {
  sessionId.value = null
  messages.value = []
}

async function loadSession(sid) {
  sessionId.value = sid
  try {
    const { data } = await getChatHistory(sid)
    messages.value = data.map(m => {
      let sources = []
      if (m.sources) {
        try { sources = JSON.parse(m.sources) } catch { /* ignore */ }
      }
      return { role: m.role, content: m.content, sources }
    })
    scrollToBottom()
  } catch (e) {
    ElMessage.error('加载对话历史失败')
  }
}

async function removeSession(sid) {
  try {
    await deleteChatSession(sid)
    if (sessionId.value === sid) {
      sessionId.value = null
      messages.value = []
    }
    await fetchSessions()
  } catch (e) {
    ElMessage.error('删除会话失败')
  }
}

async function send() {
  const q = question.value.trim()
  if (!q || sending.value) return

  messages.value.push({ role: 'user', content: q, sources: [] })
  question.value = ''
  sending.value = true
  scrollToBottom()

  try {
    const { data } = await sendMessage({
      question: q,
      knowledge_base_id: selectedKbId.value,
      session_id: sessionId.value,
    })
    sessionId.value = data.session_id
    messages.value.push({
      role: 'assistant',
      content: data.answer,
      sources: data.sources || [],
    })
    await fetchSessions()
  } catch (e) {
    ElMessage.error('发送失败: ' + (e.response?.data?.detail || e.message))
    messages.value.push({ role: 'assistant', content: '抱歉，请求出错，请稍后重试。', sources: [] })
  } finally {
    sending.value = false
    scrollToBottom()
  }
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

onMounted(() => {
  fetchKnowledgeBases()
  fetchSessions()
})

watch(selectedKbId, () => {
  fetchSessions()
})
</script>

<style scoped>
.chat-page {
  height: calc(100vh - 40px);
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chat-header h2 {
  font-size: 20px;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.chat-body {
  flex: 1;
  display: flex;
  gap: 16px;
  min-height: 0;
}

.session-list {
  width: 220px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  overflow-y: auto;
  flex-shrink: 0;
}

.session-list-header {
  padding: 12px 16px;
  font-weight: 600;
  color: #606266;
  border-bottom: 1px solid #e4e7ed;
  font-size: 14px;
}

.session-item {
  padding: 10px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #f2f3f5;
  transition: background 0.2s;
}

.session-item:hover {
  background: #f5f7fa;
}

.session-item.active {
  background: #ecf5ff;
  color: #409eff;
}

.session-title {
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.session-delete {
  opacity: 0;
  transition: opacity 0.2s;
  color: #909399;
}

.session-item:hover .session-delete {
  opacity: 1;
}

.session-empty {
  padding: 20px;
  text-align: center;
  color: #909399;
  font-size: 13px;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  min-width: 0;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.empty-chat p {
  margin-top: 12px;
  font-size: 16px;
}

.empty-chat .hint {
  font-size: 13px;
  margin-top: 4px;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: #409eff;
  color: #fff;
}

.message.assistant .message-avatar {
  background: #67c23a;
  color: #fff;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-text {
  line-height: 1.7;
  font-size: 14px;
  color: #303133;
  word-break: break-word;
}

.message-text :deep(pre) {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
}

.message-text :deep(code) {
  background: #f0f2f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}

.message-sources {
  margin-top: 8px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.sources-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.source-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin: 2px 8px 2px 0;
}

.source-score {
  font-size: 12px;
  color: #909399;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #c0c4cc;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.input-area {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  align-items: flex-end;
}

.input-area .el-textarea {
  flex: 1;
}

.input-area .el-button {
  height: 54px;
}
</style>
