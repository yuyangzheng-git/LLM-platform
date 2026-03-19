import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import Loading from '../components/Loading'
import { conversationAPI } from '../services/conversationAPI'
import { Trash2, MessageSquare } from 'lucide-react'

function HistoryPage() {
  const navigate = useNavigate()
  const [conversations, setConversations] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadConversations()
  }, [])

  const loadConversations = async () => {
    try {
      setIsLoading(true)
      const data = await conversationAPI.list()
      setConversations(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (conversationId, e) => {
    e.stopPropagation()

    if (!confirm('Are you sure you want to delete this conversation?')) {
      return
    }

    try {
      await conversationAPI.delete(conversationId)
      setConversations(conversations.filter((c) => c.id !== conversationId))
    } catch (err) {
      alert(`Failed to delete conversation: ${err.message}`)
    }
  }

  const handleOpenConversation = (conversationId) => {
    navigate(`/chat/${conversationId}`)
  }

  if (isLoading) {
    return (
      <Layout>
        <Loading message="Loading conversations..." />
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="h-screen overflow-y-auto p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          Conversation History
        </h1>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {conversations.length === 0 ? (
          <div className="text-center py-12">
            <MessageSquare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No conversations yet</p>
          </div>
        ) : (
          <div className="space-y-4">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => handleOpenConversation(conversation.id)}
                className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer border border-gray-200"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-800 mb-1">
                      {conversation.title}
                    </h3>
                    <p className="text-sm text-gray-600 mb-2">
                      {conversation.model_provider} / {conversation.model_name}
                    </p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span>{conversation.message_count} messages</span>
                      <span>{conversation.total_tokens} tokens</span>
                      <span>
                        {new Date(conversation.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={(e) => handleDelete(conversation.id, e)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}

export default HistoryPage
