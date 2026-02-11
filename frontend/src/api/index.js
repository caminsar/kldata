import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

// ---- 知识库 ----
export const getKnowledgeBases = () => api.get('/knowledge-bases')
export const createKnowledgeBase = (data) => api.post('/knowledge-bases', data)
export const updateKnowledgeBase = (id, data) => api.put(`/knowledge-bases/${id}`, data)
export const deleteKnowledgeBase = (id) => api.delete(`/knowledge-bases/${id}`)

// ---- 文档 ----
export const getDocuments = (kbId) => api.get(`/documents/${kbId}`)
export const uploadDocument = (kbId, file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/documents/${kbId}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress,
  })
}
export const deleteDocument = (docId) => api.delete(`/documents/file/${docId}`)
export const reprocessDocument = (docId) => api.post(`/documents/file/${docId}/reprocess`)

// ---- 对话 ----
export const sendMessage = (data) => api.post('/chat', data)
export const getChatHistory = (sessionId) => api.get(`/chat/history/${sessionId}`)
export const getChatSessions = (kbId) => api.get('/chat/sessions', { params: { knowledge_base_id: kbId } })
export const deleteChatSession = (sessionId) => api.delete(`/chat/sessions/${sessionId}`)

// ---- 系统 ----
export const getSystemConfig = () => api.get('/system/config')
export const updateSystemConfig = (data) => api.put('/system/config', data)
export const healthCheck = () => api.get('/system/health')

export default api
