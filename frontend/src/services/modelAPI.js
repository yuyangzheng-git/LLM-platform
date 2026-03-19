import api from './api'

export const modelAPI = {
  /**
   * Get all providers (list all model configurations)
   */
  getProviders: async () => {
    try {
      const configs = await api.get('/models/configs')
      // Transform to provider format expected by frontend
      return configs.map(config => ({
        provider: config.provider,
        api_key_configured: config.enabled,
        available_models: config.available_models || [],
        is_active: config.enabled,
        default_model: config.default_model
      }))
    } catch (error) {
      console.error('Failed to get providers:', error)
      return []
    }
  },

  /**
   * List all model configurations
   */
  listConfigs: async () => {
    return api.get('/models/configs')
  },

  /**
   * Create or update model configuration
   */
  createOrUpdateConfig: async (data) => {
    return api.post('/models/configs', data)
  },

  /**
   * Get configuration for a specific provider
   */
  getConfig: async (provider) => {
    return api.get(`/models/configs/${provider}`)
  },

  /**
   * Update model configuration
   */
  updateConfig: async (provider, data) => {
    return api.put(`/models/configs/${provider}`, data)
  },

  /**
   * Delete model configuration
   */
  deleteConfig: async (provider) => {
    return api.delete(`/models/configs/${provider}`)
  },

  /**
   * Test connection to model provider
   */
  testConnection: async (provider) => {
    return api.post(`/models/test/${provider}`)
  },

  /**
   * Get available models for a provider
   */
  getAvailableModels: async (provider) => {
    return api.get(`/models/available/${provider}`)
  },
}

export default modelAPI
