import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import Loading from '../components/Loading'
import { modelAPI } from '../services/modelAPI'
import { conversationAPI } from '../services/conversationAPI'
import { Check, X } from 'lucide-react'

function SettingsPage() {
  const navigate = useNavigate()

  const [providers, setProviders] = useState(['openai', 'anthropic', 'gemini', 'generic'])
  const [configs, setConfigs] = useState({})
  const [selectedProvider, setSelectedProvider] = useState('openai')
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [testResults, setTestResults] = useState({})

  // New conversation form
  const [showNewConversation, setShowNewConversation] = useState(false)
  const [newConvForm, setNewConvForm] = useState({
    title: '',
    model_provider: 'openai',
    model_name: 'gpt-3.5-turbo',
    system_prompt: '',
    temperature: 0.7,
    max_tokens: 2000,
  })

  useEffect(() => {
    loadConfigs()
  }, [])

  const loadConfigs = async () => {
    try {
      setIsLoading(true)
      const data = await modelAPI.listConfigs()
      const configMap = {}
      data.forEach((config) => {
        configMap[config.provider] = config
      })
      setConfigs(configMap)
    } catch (err) {
      console.error('Failed to load configs:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSaveConfig = async (provider) => {
    const config = configs[provider]
    if (!config || !config.api_key) {
      alert('API key is required')
      return
    }

    setIsSaving(true)
    try {
      await modelAPI.createOrUpdateConfig({
        provider: provider,
        api_key: config.api_key,
        api_base_url: config.api_base_url,
        organization_id: config.organization_id,
        default_model: config.default_model,
        default_temperature: config.default_temperature || 0.7,
        default_max_tokens: config.default_max_tokens || 2000,
        enabled: config.enabled !== false,
      })
      alert('Configuration saved successfully')
      loadConfigs()
    } catch (err) {
      alert(`Failed to save configuration: ${err.message}`)
    } finally {
      setIsSaving(false)
    }
  }

  const handleTestConnection = async (provider) => {
    try {
      const result = await modelAPI.testConnection(provider)
      setTestResults((prev) => ({
        ...prev,
        [provider]: result,
      }))
    } catch (err) {
      setTestResults((prev) => ({
        ...prev,
        [provider]: { connected: false, message: err.message },
      }))
    }
  }

  const handleCreateConversation = async () => {
    if (!newConvForm.title || !newConvForm.model_name) {
      alert('Title and model are required')
      return
    }

    try {
      const conversation = await conversationAPI.create(newConvForm)
      navigate(`/chat/${conversation.id}`)
    } catch (err) {
      alert(`Failed to create conversation: ${err.message}`)
    }
  }

  const currentConfig = configs[selectedProvider] || {
    provider: selectedProvider,
    api_key: '',
    api_base_url: '',
    organization_id: '',
    default_model: '',
    default_temperature: 0.7,
    default_max_tokens: 2000,
    enabled: true,
  }

  if (isLoading) {
    return (
      <Layout>
        <Loading message="Loading settings..." />
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="h-screen overflow-y-auto p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Settings</h1>

        {/* New Conversation Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            New Conversation
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Title
              </label>
              <input
                type="text"
                value={newConvForm.title}
                onChange={(e) =>
                  setNewConvForm({ ...newConvForm, title: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="My Conversation"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Provider
                </label>
                <select
                  value={newConvForm.model_provider}
                  onChange={(e) =>
                    setNewConvForm({
                      ...newConvForm,
                      model_provider: e.target.value,
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  {providers.map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Model
                </label>
                <input
                  type="text"
                  value={newConvForm.model_name}
                  onChange={(e) =>
                    setNewConvForm({ ...newConvForm, model_name: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="gpt-3.5-turbo"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                System Prompt (optional)
              </label>
              <textarea
                value={newConvForm.system_prompt}
                onChange={(e) =>
                  setNewConvForm({
                    ...newConvForm,
                    system_prompt: e.target.value,
                  })
                }
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="You are a helpful assistant..."
              />
            </div>

            <button
              onClick={handleCreateConversation}
              className="w-full bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600 transition-colors"
            >
              Create Conversation
            </button>
          </div>
        </div>

        {/* Model Configuration Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            Model Configuration
          </h2>

          {/* Provider Tabs */}
          <div className="flex space-x-2 mb-6 border-b">
            {providers.map((provider) => (
              <button
                key={provider}
                onClick={() => setSelectedProvider(provider)}
                className={`px-4 py-2 font-medium transition-colors ${
                  selectedProvider === provider
                    ? 'text-primary-600 border-b-2 border-primary-600'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                {provider}
              </button>
            ))}
          </div>

          {/* Configuration Form */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                API Key *
              </label>
              <input
                type="password"
                value={currentConfig.api_key || ''}
                onChange={(e) =>
                  setConfigs({
                    ...configs,
                    [selectedProvider]: {
                      ...currentConfig,
                      api_key: e.target.value,
                    },
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="sk-..."
              />
            </div>

            {selectedProvider === 'generic' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Base URL
                </label>
                <input
                  type="text"
                  value={currentConfig.api_base_url || ''}
                  onChange={(e) =>
                    setConfigs({
                      ...configs,
                      [selectedProvider]: {
                        ...currentConfig,
                        api_base_url: e.target.value,
                      },
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="http://localhost:8000/v1"
                />
              </div>
            )}

            <div className="flex space-x-4">
              <button
                onClick={() => handleSaveConfig(selectedProvider)}
                disabled={isSaving}
                className="flex-1 bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600 transition-colors disabled:bg-gray-300"
              >
                {isSaving ? 'Saving...' : 'Save Configuration'}
              </button>

              <button
                onClick={() => handleTestConnection(selectedProvider)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Test Connection
              </button>
            </div>

            {testResults[selectedProvider] && (
              <div
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
                  testResults[selectedProvider].connected
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}
              >
                {testResults[selectedProvider].connected ? (
                  <Check className="w-5 h-5" />
                ) : (
                  <X className="w-5 h-5" />
                )}
                <span>{testResults[selectedProvider].message}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default SettingsPage
