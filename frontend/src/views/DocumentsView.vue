<template>
  <div class="docs-page">
    <div class="page-header">
      <h2>文档管理</h2>
      <div class="header-actions">
        <el-select v-model="selectedKbId" placeholder="选择知识库" style="width: 220px" @change="fetchDocuments">
          <el-option v-for="kb in knowledgeBases" :key="kb.id" :label="kb.name" :value="kb.id" />
        </el-select>
      </div>
    </div>

    <el-card v-if="selectedKbId">
      <!-- 上传区域 -->
      <el-upload
        class="upload-area"
        drag
        :action="`/api/documents/${selectedKbId}/upload`"
        :on-success="onUploadSuccess"
        :on-error="onUploadError"
        :before-upload="beforeUpload"
        :show-file-list="false"
        multiple
        accept=".pdf,.docx,.doc,.txt,.md,.csv,.html"
      >
        <el-icon :size="40" color="#c0c4cc"><UploadFilled /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 PDF, DOCX, TXT, MD, CSV, HTML 格式，单文件最大 50MB</div>
        </template>
      </el-upload>

      <!-- 文档列表 -->
      <el-table :data="documents" style="width: 100%; margin-top: 20px" v-loading="loading">
        <el-table-column prop="filename" label="文件名" min-width="200" />
        <el-table-column prop="file_type" label="类型" width="80" />
        <el-table-column label="大小" width="100">
          <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column prop="chunk_count" label="分块数" width="80" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="上传时间" width="170">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="reprocess(row)" :loading="row._reprocessing">
              重新处理
            </el-button>
            <el-button size="small" text type="danger" @click="confirmDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-empty v-else description="请先选择一个知识库" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getKnowledgeBases, getDocuments, deleteDocument, reprocessDocument } from '../api'

const route = useRoute()
const knowledgeBases = ref([])
const selectedKbId = ref(null)
const documents = ref([])
const loading = ref(false)

async function fetchKBs() {
  try {
    const { data } = await getKnowledgeBases()
    knowledgeBases.value = data
    if (route.query.kb) {
      selectedKbId.value = Number(route.query.kb)
      await fetchDocuments()
    }
  } catch { /* ignore */ }
}

async function fetchDocuments() {
  if (!selectedKbId.value) return
  loading.value = true
  try {
    const { data } = await getDocuments(selectedKbId.value)
    documents.value = data
  } catch (e) {
    ElMessage.error('获取文档列表失败')
  } finally {
    loading.value = false
  }
}

function beforeUpload(file) {
  const maxSize = 50 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.warning('文件大小不能超过 50MB')
    return false
  }
  return true
}

function onUploadSuccess() {
  ElMessage.success('上传成功')
  fetchDocuments()
}

function onUploadError() {
  ElMessage.error('上传失败')
}

async function reprocess(row) {
  row._reprocessing = true
  try {
    await reprocessDocument(row.id)
    ElMessage.success('重新处理完成')
    await fetchDocuments()
  } catch (e) {
    ElMessage.error('处理失败')
  } finally {
    row._reprocessing = false
  }
}

async function confirmDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除文档「${row.filename}」？`, '删除确认', { type: 'warning' })
    await deleteDocument(row.id)
    ElMessage.success('已删除')
    await fetchDocuments()
  } catch { /* cancelled */ }
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function formatDate(d) {
  return new Date(d).toLocaleString('zh-CN')
}

function statusType(s) {
  return { completed: 'success', processing: 'warning', failed: 'danger', pending: 'info' }[s] || 'info'
}

function statusText(s) {
  return { completed: '已完成', processing: '处理中', failed: '失败', pending: '等待中' }[s] || s
}

onMounted(fetchKBs)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 20px;
  color: #303133;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
}
</style>
