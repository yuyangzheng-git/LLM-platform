import { useState, useCallback } from 'react'
import { useSSE } from './useSSE'
import { chatAPI } from '../services/chatAPI'

/**
 * Hook for managing chat functionality
 */
export const useChat = (conversationId) => {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [currentResponse, setCurrentResponse] = useState('')

  const { connect } = useSSE()

  /**
   * Send a chat message with streaming
   */
  const sendMessage = useCallback(async (message, fileIds = []) => {
    if (!message.trim()) return

    setIsLoading(true)
    setError(null)
    setCurrentResponse('')

    // Add user message to UI immediately
    const userMessage = {
      role: 'user',
      content: message,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMessage])

    try {
      // Prepare fetch options for streaming
      // 生产环境：空字符串（通过 Nginx 代理）
      // 开发环境：http://localhost:3211
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL !== undefined
        ? import.meta.env.VITE_API_BASE_URL
        : 'http://localhost:3211'

      await connect(`${API_BASE_URL}/api/v1/chat/stream`, {
        fetchOptions: {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            conversation_id: conversationId,
            message: message,
            file_ids: fileIds,
            stream: true,
          }),
        },
        onMessage: (data) => {
          if (data.type === 'chunk') {
            // Append chunk to current response
            setCurrentResponse((prev) => prev + data.content)
          } else if (data.type === 'done') {
            // Finalize assistant message
            const assistantMessage = {
              id: data.message_id,
              role: 'assistant',
              content: currentResponse,
              created_at: new Date().toISOString(),
              tokens: data.tokens,
            }
            setMessages((prev) => [...prev, assistantMessage])
            setCurrentResponse('')
            setIsLoading(false)
          } else if (data.type === 'error' || data.error) {
            setError(data.error || 'An error occurred')
            setIsLoading(false)
          }
        },
        onError: (err) => {
          setError(err.message)
          setIsLoading(false)
        },
        onClose: () => {
          setIsLoading(false)
        },
      })
    } catch (err) {
      setError(err.message)
      setIsLoading(false)
    }
  }, [conversationId, connect, currentResponse])

  /**
   * Clear current chat
   */
  const clearMessages = useCallback(() => {
    setMessages([])
    setCurrentResponse('')
    setError(null)
  }, [])

  return {
    messages,
    currentResponse,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    setMessages, // Allow external updates to messages
  }
}

export default useChat
