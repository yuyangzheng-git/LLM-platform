import { useState, useEffect, useRef } from 'react'
import { Menu } from 'lucide-react'
import { ConversationSidebar } from './ConversationSidebar'
import { MainChatArea } from './MainChatArea'
import { ChatHeader } from './ChatHeader'
import { IconButton } from '../common/IconButton'
import { conversationAPI } from '../../services/conversationAPI'
import { fileAPI } from '../../services/fileAPI'
import { chatAPI } from '../../services/chatAPI'

export function UnifiedChatInterface() {
  // UI State
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isStarted, setIsStarted] = useState(false)

  // Chat State
  const [inputMessage, setInputMessage] = useState('')
  const [selectedFiles, setSelectedFiles] = useState([])
  const [uploadedFileIds, setUploadedFileIds] = useState([])
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [currentToolCalls, setCurrentToolCalls] = useState([])

  // Conversation State
  const [conversationId, setConversationId] = useState(null)
  const [conversations, setConversations] = useState([])

  // Model State - 默认使用GPT-4o
  const [selectedModel, setSelectedModel] = useState('gpt-4o')

  const fileInputRef = useRef(null)

  // Load initial data
  useEffect(() => {
    loadConversations()
  }, [])

  const loadConversations = async () => {
    try {
      const data = await conversationAPI.list()
      setConversations(data)
    } catch (err) {
      console.error('Failed to load conversations:', err)
    }
  }

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files)
    setSelectedFiles((prev) => [...prev, ...files])

    setIsUploading(true)
    setUploadProgress(0)
    try {
      const uploadedFiles = await fileAPI.uploadBatch(files, null, (progress) => {
        setUploadProgress(progress)
      })
      const fileIds = uploadedFiles.map((f) => f.id)
      setUploadedFileIds((prev) => [...prev, ...fileIds])
    } catch (err) {
      console.error('File upload failed:', err)
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
    }
  }

  const removeFile = (index) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index))
    setUploadedFileIds((prev) => prev.filter((_, i) => i !== index))
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() && uploadedFileIds.length === 0) return

    const messageToSend = inputMessage
    const filesToSend = uploadedFileIds

    // Clear input immediately
    setInputMessage('')
    setSelectedFiles([])
    setUploadedFileIds([])

    // Start conversation if not started
    if (!isStarted) {
      setIsStarted(true)
    }

    // Add user message immediately with file indicators
    const userMessage = {
      role: 'user',
      content: messageToSend,
      created_at: new Date().toISOString(),
      fileCount: filesToSend.length,
    }
    setMessages((prev) => [...prev, userMessage])

    // Show loading indicator
    setIsLoading(true)

    // Create new conversation if needed
    let convId = conversationId
    if (!convId) {
      try {
        const newConv = await conversationAPI.create({
          title: messageToSend.slice(0, 50),
          model_provider: 'openai',
          model_name: selectedModel,
        })
        convId = newConv.id
        setConversationId(convId)
        loadConversations()
      } catch (err) {
        console.error('Failed to create conversation:', err)
        setIsLoading(false)
        return
      }
    }

    // Send message with streaming
    try {
      let fullResponse = ''
      let fullReasoning = ''
      let hasReceivedFirstChunk = false

      // Reset tool calls for new response
      setCurrentToolCalls([])

      // Add empty assistant message first
      const assistantMessageIndex = messages.length + 1
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: '',
        reasoning: '',
        tool_calls: [],
        created_at: new Date().toISOString(),
      }])

      await chatAPI.streamChat(
        convId,
        messageToSend,
        (chunk) => {
          // Hide loading indicator after first chunk
          if (!hasReceivedFirstChunk) {
            hasReceivedFirstChunk = true
            setIsLoading(false)
          }

          fullResponse += chunk
          // Update immediately on every chunk
          setMessages((prev) => {
            const updated = [...prev]
            if (updated[assistantMessageIndex]) {
              updated[assistantMessageIndex] = {
                ...updated[assistantMessageIndex],
                content: fullResponse
              }
            }
            return updated
          })
        },
        filesToSend,
        // Reasoning callback
        (reasoningChunk) => {
          fullReasoning += reasoningChunk
          // Update reasoning content
          setMessages((prev) => {
            const updated = [...prev]
            if (updated[assistantMessageIndex]) {
              updated[assistantMessageIndex] = {
                ...updated[assistantMessageIndex],
                reasoning: fullReasoning
              }
            }
            return updated
          })
        },
        // Tool call callback
        (toolCall) => {
          setCurrentToolCalls((prev) => [...prev, {
            ...toolCall,
            status: 'calling'
          }])
        },
        // Tool result callback
        (toolResult) => {
          setCurrentToolCalls((prev) =>
            prev.map((call) =>
              call.id === toolResult.tool_id
                ? {
                    ...call,
                    status: toolResult.success ? 'completed' : 'error',
                    result: toolResult.result,
                    error: toolResult.error
                  }
                : call
            )
          )
        }
      )

      // After streaming completes, save tool calls to message
      setMessages((prev) => {
        const updated = [...prev]
        if (updated[assistantMessageIndex]) {
          updated[assistantMessageIndex] = {
            ...updated[assistantMessageIndex],
            tool_calls: currentToolCalls.length > 0 ? currentToolCalls : undefined
          }
        }
        return updated
      })

      // Ensure loading is hidden at the end
      setIsLoading(false)
    } catch (err) {
      console.error('Failed to send message:', err)
      setIsLoading(false)
      // Update last message with error
      setMessages((prev) => {
        const updated = [...prev]
        const lastIdx = updated.length - 1
        if (updated[lastIdx] && updated[lastIdx].role === 'assistant') {
          updated[lastIdx] = {
            ...updated[lastIdx],
            content: '抱歉，发生了错误。请稍后重试。',
            isError: true
          }
        }
        return updated
      })
    }
  }

  const handleNewChat = () => {
    setConversationId(null)
    setMessages([])
    setIsStarted(false)
    setInputMessage('')
    setSelectedFiles([])
    setUploadedFileIds([])
    setSidebarOpen(false)
  }

  const loadConversation = async (id) => {
    try {
      const data = await conversationAPI.getMessages(id)
      setConversationId(id)
      setMessages(data)
      setIsStarted(true)
      setSidebarOpen(false)
    } catch (err) {
      console.error('Failed to load conversation:', err)
    }
  }

  const deleteConversation = async (id) => {
    if (!confirm('确定要删除这个对话吗？')) return

    try {
      await conversationAPI.delete(id)

      // If deleting current conversation, start new chat
      if (id === conversationId) {
        handleNewChat()
      }

      // Reload conversations list
      loadConversations()
    } catch (err) {
      console.error('Failed to delete conversation:', err)
      alert('删除对话失败，请重试')
    }
  }

  const exportConversation = (format) => {
    if (!conversationId || messages.length === 0) return

    const content = messages.map((m) => `${m.role.toUpperCase()}:\n${m.content}\n\n`).join('')
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `conversation-${conversationId}.${format}`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="h-full flex overflow-hidden">
      {/* Conversation Sidebar */}
      <ConversationSidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        conversations={conversations}
        currentConversationId={conversationId}
        onSelectConversation={loadConversation}
        onDeleteConversation={deleteConversation}
        onNewChat={handleNewChat}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-full">
        {/* Top Bar - 合并后的单一顶栏 */}
        <div className="flex-shrink-0 p-2 sm:p-3 md:p-4 flex items-center justify-between bg-white/50 dark:bg-bg-secondary/50 backdrop-blur-xl border-b border-border-primary">
          <div className="flex items-center space-x-2">
            <IconButton
              icon={Menu}
              onClick={() => setSidebarOpen(true)}
              label="打开对话历史"
            />
          </div>

          <div className="flex items-center space-x-2 md:space-x-3">
            {isStarted && selectedModel && (
              <div className="bg-gradient-to-r from-orange-100 to-amber-100 dark:from-orange-900/30 dark:to-amber-900/30 px-3 sm:px-4 md:px-6 py-1.5 md:py-2 rounded-xl md:rounded-2xl border border-orange-300/50 dark:border-amber-400/30">
                <div className="text-xs sm:text-sm font-semibold bg-gradient-to-r from-orange-600 via-amber-600 to-rose-600 dark:from-amber-400 dark:via-orange-400 dark:to-rose-400 bg-clip-text text-transparent whitespace-nowrap">
                  {selectedModel}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Main Chat Area - takes remaining height */}
        <div className="flex-1 overflow-hidden">
          <MainChatArea
            messages={messages}
            inputMessage={inputMessage}
            onInputChange={setInputMessage}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            selectedFiles={selectedFiles}
            onFileSelect={handleFileSelect}
            onRemoveFile={removeFile}
            isUploading={isUploading}
            uploadProgress={uploadProgress}
            isStarted={isStarted}
            selectedModel={selectedModel}
            onModelChange={setSelectedModel}
            currentToolCalls={currentToolCalls}
          />
        </div>
      </div>
    </div>
  )
}
