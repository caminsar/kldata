<template>
  <div class="kb-page">
    <div class="page-header">
      <h2>知识库管理</h2>
      <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">新建知识库</el-button>
    </div>

    <el-row :gutter="16">
      <el-col v-for="kb in knowledgeBases" :key="kb.id" :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="kb-card" shadow="hover">
          <template #header>
            <div class="kb-card-header">
              <span class="kb-name">{{ kb.name }}</span>
              <el-dropdown trigger="click">
                <el-icon class="more-btn"><MoreFilled /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="editKb(kb)">
                      <el-icon><Edit /></el-icon>编辑
                    </el-dropdown-item>
                    <el-dropdown-item @click="confirmDelete(kb)" divided>
                      <el-icon color="#f56c6c"><Delete /></el-icon>
                      <span style="color:#f56c6c">删除</span>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
          <p class="kb-desc">{{ kb.description || '暂无描述' }}</p>
          <div class="kb-meta">
            <span><el-icon><Document /></el-icon> {{ kb.document_count }} 篇文档</span>
            <span><el-icon><Clock /></el-icon> {{ formatDate(kb.created_at) }}</span>
          </div>
          <div class="kb-actions">
            <el-button size="small" type="primary" plain @click="goChat(kb)">
              <el-icon><ChatDotRound /></el-icon> 对话
            </el-button>
            <el-button size="small" plain @click="goDocs(kb)">
              <el-icon><Upload /></el-icon> 文档
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="knowledgeBases.length === 0" description="暂无知识库，点击上方按钮创建" />

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingKb ? '编辑知识库' : '新建知识库'"
      width="480px"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="输入知识库名称" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="输入描述（可选）" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ editingKb ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, MoreFilled, Edit, Delete, Document, Clock, ChatDotRound, Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getKnowledgeBases, createKnowledgeBase, updateKnowledgeBase, deleteKnowledgeBase } from '../api'

const router = useRouter()
const knowledgeBases = ref([])
const showCreateDialog = ref(false)
const editingKb = ref(null)
const submitting = ref(false)
const form = ref({ name: '', description: '' })

async function fetchData() {
  try {
    const { data } = await getKnowledgeBases()
    knowledgeBases.value = data
  } catch (e) {
    ElMessage.error('获取知识库列表失败')
  }
}

function editKb(kb) {
  editingKb.value = kb
  form.value = { name: kb.name, description: kb.description }
  showCreateDialog.value = true
}

async function submitForm() {
  if (!form.value.name.trim()) {
    ElMessage.warning('请输入知识库名称')
    return
  }
  submitting.value = true
  try {
    if (editingKb.value) {
      await updateKnowledgeBase(editingKb.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await createKnowledgeBase(form.value)
      ElMessage.success('创建成功')
    }
    showCreateDialog.value = false
    editingKb.value = null
    form.value = { name: '', description: '' }
    await fetchData()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function confirmDelete(kb) {
  try {
    await ElMessageBox.confirm(`确定删除知识库「${kb.name}」？所有文档和对话记录都将被删除，此操作不可恢复。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      confirmButtonClass: 'el-button--danger',
    })
    await deleteKnowledgeBase(kb.id)
    ElMessage.success('已删除')
    await fetchData()
  } catch { /* cancelled */ }
}

function goChat(kb) {
  router.push({ path: '/chat', query: { kb: kb.id } })
}

function goDocs(kb) {
  router.push({ path: '/documents', query: { kb: kb.id } })
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('zh-CN')
}

onMounted(fetchData)
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

.kb-card {
  margin-bottom: 16px;
}

.kb-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kb-name {
  font-weight: 600;
  font-size: 15px;
}

.more-btn {
  cursor: pointer;
  color: #909399;
}

.kb-desc {
  font-size: 13px;
  color: #909399;
  margin-bottom: 12px;
  min-height: 40px;
}

.kb-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
}

.kb-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.kb-actions {
  display: flex;
  gap: 8px;
}
</style>
