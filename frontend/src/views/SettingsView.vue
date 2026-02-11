<template>
  <div class="settings-page">
    <h2>系统设置</h2>

    <el-card class="settings-card" v-loading="loading">
      <el-form :model="config" label-width="140px" label-position="right">
        <el-divider content-position="left">LLM 配置</el-divider>

        <el-form-item label="LLM 提供者">
          <el-select v-model="config.llm_provider" style="width: 300px">
            <el-option label="OpenAI (兼容接口)" value="openai" />
            <el-option label="Ollama (本地模型)" value="ollama" />
          </el-select>
        </el-form-item>

        <el-form-item label="模型名称">
          <el-input v-model="config.llm_model" placeholder="如 gpt-4o, qwen2.5:7b" style="width: 300px" />
        </el-form-item>

        <el-form-item label="API Key" v-if="config.llm_provider === 'openai'">
          <el-input v-model="config.llm_api_key" type="password" show-password placeholder="OpenAI API Key" style="width: 300px" />
        </el-form-item>

        <el-form-item label="API 地址" v-if="config.llm_provider === 'openai'">
          <el-input v-model="config.llm_api_base" placeholder="留空使用默认地址" style="width: 300px" />
        </el-form-item>

        <el-form-item label="Temperature">
          <el-slider v-model="config.llm_temperature" :min="0" :max="2" :step="0.1" style="width: 300px" show-input />
        </el-form-item>

        <el-form-item label="最大 Token 数">
          <el-input-number v-model="config.llm_max_tokens" :min="100" :max="32000" :step="100" />
        </el-form-item>

        <el-divider content-position="left">Embedding 配置</el-divider>

        <el-form-item label="Embedding 提供者">
          <el-select v-model="config.embedding_provider" style="width: 300px">
            <el-option label="OpenAI" value="openai" />
            <el-option label="Ollama" value="ollama" />
            <el-option label="HuggingFace (本地)" value="huggingface" />
          </el-select>
        </el-form-item>

        <el-form-item label="Embedding 模型">
          <el-input v-model="config.embedding_model" placeholder="如 text-embedding-3-small" style="width: 300px" />
        </el-form-item>

        <el-divider content-position="left">检索配置</el-divider>

        <el-form-item label="检索数量 (Top K)">
          <el-input-number v-model="config.retrieval_top_k" :min="1" :max="20" />
        </el-form-item>

        <el-form-item label="相关度阈值">
          <el-slider v-model="config.retrieval_score_threshold" :min="0" :max="1" :step="0.05" style="width: 300px" show-input />
        </el-form-item>

        <el-divider content-position="left">文档处理配置</el-divider>

        <el-form-item label="分块大小">
          <el-input-number v-model="config.chunk_size" :min="100" :max="4000" :step="50" />
        </el-form-item>

        <el-form-item label="分块重叠">
          <el-input-number v-model="config.chunk_overlap" :min="0" :max="500" :step="10" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveConfig" :loading="saving">保存配置</el-button>
          <el-button @click="fetchConfig">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSystemConfig, updateSystemConfig } from '../api'

const loading = ref(false)
const saving = ref(false)
const config = ref({
  llm_provider: 'openai',
  llm_model: '',
  llm_api_key: '',
  llm_api_base: '',
  llm_temperature: 0.7,
  llm_max_tokens: 2000,
  embedding_provider: 'openai',
  embedding_model: '',
  retrieval_top_k: 5,
  retrieval_score_threshold: 0.5,
  chunk_size: 500,
  chunk_overlap: 50,
})

async function fetchConfig() {
  loading.value = true
  try {
    const { data } = await getSystemConfig()
    config.value.llm_provider = data.llm_provider
    config.value.llm_model = data.llm_model
    config.value.embedding_provider = data.embedding_provider
    config.value.embedding_model = data.embedding_model
    config.value.retrieval_top_k = data.retrieval_top_k
    config.value.retrieval_score_threshold = data.retrieval_score_threshold
    config.value.chunk_size = data.chunk_size
    config.value.chunk_overlap = data.chunk_overlap
  } catch (e) {
    ElMessage.error('获取配置失败')
  } finally {
    loading.value = false
  }
}

async function saveConfig() {
  saving.value = true
  try {
    await updateSystemConfig(config.value)
    ElMessage.success('配置已保存')
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

onMounted(fetchConfig)
</script>

<style scoped>
.settings-page h2 {
  font-size: 20px;
  color: #303133;
  margin-bottom: 20px;
}

.settings-card {
  max-width: 700px;
}
</style>
