import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getKnowledgeBases } from '../api'

export const useAppStore = defineStore('app', () => {
  const knowledgeBases = ref([])
  const currentKbId = ref(null)
  const loading = ref(false)

  async function fetchKnowledgeBases() {
    try {
      const { data } = await getKnowledgeBases()
      knowledgeBases.value = data
    } catch (e) {
      console.error('获取知识库列表失败:', e)
    }
  }

  function setCurrentKb(id) {
    currentKbId.value = id
  }

  return { knowledgeBases, currentKbId, loading, fetchKnowledgeBases, setCurrentKb }
})
