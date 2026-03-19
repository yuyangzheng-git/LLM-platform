import api from './api'

export const conversationAPI = {
  /**
   * Create a new conversation
   */
  create: async (data) => {
    return api.post('/conversations', data)
  },

  /**
   * List all conversations
   */
  list: async (skip = 0, limit = 50) => {
    return api.get('/conversations', { params: { skip, limit } })
  },

  /**
   * Get a specific conversation
   */
  get: async (conversationId) => {
    return api.get(`/conversations/${conversationId}`)
  },

  /**
   * Update a conversation
   */
  update: async (conversationId, data) => {
    return api.put(`/conversations/${conversationId}`, data)
  },

  /**
   * Delete a conversation
   */
  delete: async (conversationId) => {
    return api.delete(`/conversations/${conversationId}`)
  },

  /**
   * Get messages for a conversation
   */
  getMessages: async (conversationId, skip = 0, limit = 100) => {
    return api.get(`/conversations/${conversationId}/messages`, {
      params: { skip, limit },
    })
  },
}

export default conversationAPI
