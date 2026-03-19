import { useState, useEffect, useCallback } from 'react'

/**
 * Hook for handling Server-Sent Events (SSE)
 */
export const useSSE = () => {
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState(null)

  const connect = useCallback(async (url, options = {}) => {
    const {
      onMessage,
      onError,
      onOpen,
      onClose,
    } = options

    try {
      setError(null)
      setIsConnected(false)

      // Use fetch with ReadableStream for SSE
      const response = await fetch(url, options.fetchOptions || {})

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      if (onOpen) onOpen()
      setIsConnected(true)

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          if (onClose) onClose()
          setIsConnected(false)
          break
        }

        buffer += decoder.decode(value, { stream: true })

        // Process complete SSE messages
        const lines = buffer.split('\n\n')
        buffer = lines.pop() || '' // Keep incomplete message in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            try {
              const parsed = JSON.parse(data)
              if (onMessage) onMessage(parsed)
            } catch (e) {
              console.error('Failed to parse SSE data:', e)
            }
          }
        }
      }
    } catch (err) {
      console.error('SSE connection error:', err)
      setError(err.message)
      if (onError) onError(err)
      setIsConnected(false)
    }
  }, [])

  return {
    connect,
    isConnected,
    error,
  }
}

export default useSSE
