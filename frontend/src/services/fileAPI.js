import axios from 'axios'

// 生产环境：空字符串（通过 Nginx 代理）
// 开发环境：http://localhost:3211
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL !== undefined
  ? import.meta.env.VITE_API_BASE_URL
  : 'http://localhost:3211'

export const fileAPI = {
  /**
   * Upload a single file
   */
  upload: async (file, messageId = null) => {
    const formData = new FormData()
    formData.append('file', file)
    if (messageId) {
      formData.append('message_id', messageId)
    }

    const response = await axios.post(
      `${API_BASE_URL}/api/v1/files/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    return response.data
  },

  /**
   * Upload multiple files
   */
  uploadBatch: async (files, messageId = null, onProgress = null) => {
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })
    if (messageId) {
      formData.append('message_id', messageId)
    }

    const response = await axios.post(
      `${API_BASE_URL}/api/v1/files/upload/batch`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            onProgress(percentCompleted)
          }
        },
      }
    )

    return response.data
  },

  /**
   * Get file information
   */
  get: async (fileId) => {
    const response = await axios.get(
      `${API_BASE_URL}/api/v1/files/${fileId}`
    )
    return response.data
  },

  /**
   * Delete a file
   */
  delete: async (fileId) => {
    await axios.delete(`${API_BASE_URL}/api/v1/files/${fileId}`)
  },
}

export default fileAPI
