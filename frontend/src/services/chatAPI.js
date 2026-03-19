import api from './api'

export const chatAPI = {
  /**
   * Send a chat message with streaming
   * @param {string} conversationId - Conversation ID
   * @param {string} message - User message
   * @param {function} onChunk - Callback for each content chunk
   * @param {array} fileIds - Array of file IDs
   * @param {function} onReasoning - Optional callback for reasoning chunks
   * @param {function} onToolCall - Optional callback for tool call events
   * @param {function} onToolResult - Optional callback for tool result events
   */
  streamChat: async (conversationId, message, onChunk, fileIds = [], onReasoning = null, onToolCall = null, onToolResult = null) => {
    // 生产环境：空字符串（通过 Nginx 代理）
    // 开发环境：http://localhost:3211
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL !== undefined
      ? import.meta.env.VITE_API_BASE_URL
      : 'http://localhost:3211'

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/stream`, {
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
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          break
        }

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()

            if (data === '[DONE]') {
              return
            }

            try {
              const parsed = JSON.parse(data)

              // Handle tool call events
              if (parsed.type === 'tool_call' && onToolCall) {
                onToolCall({
                  id: parsed.tool_id,
                  name: parsed.tool_name,
                  arguments: parsed.arguments,
                  status: 'calling'
                })
              }
              // Handle tool result events
              else if (parsed.type === 'tool_result' && onToolResult) {
                onToolResult({
                  tool_id: parsed.tool_id,
                  success: parsed.success,
                  result: parsed.result,
                  error: parsed.error
                })
              }
              // Handle reasoning chunks (thinking process)
              else if (parsed.type === 'reasoning' && parsed.content && onReasoning) {
                onReasoning(parsed.content)
              }
              // Handle regular content chunks
              else if (parsed.type === 'chunk' && parsed.content) {
                onChunk(parsed.content)
              }
              // Backward compatibility - no type specified
              else if (parsed.content && !parsed.type) {
                onChunk(parsed.content)
              }
            } catch (e) {
              // If not JSON, treat as plain text
              if (data) {
                onChunk(data)
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Stream chat error:', error)
      throw error
    }
  },

  /**
   * Send a chat message without streaming
   */
  completeChat: async (conversationId, message, fileIds = []) => {
    return api.post('/chat/complete', {
      conversation_id: conversationId,
      message: message,
      file_ids: fileIds,
      stream: false,
    })
  },
}

export default chatAPI
