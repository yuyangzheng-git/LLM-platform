import { useState, useEffect, useRef, useCallback } from 'react'
import { History } from 'lucide-react'
import { ConversationSidebar } from './ConversationSidebar'
import { MainChatArea } from './MainChatArea'
import { IconButton } from '../common/IconButton'
import { conversationAPI } from '../../services/conversationAPI'
import { fileAPI } from '../../services/fileAPI'
import { chatAPI } from '../../services/chatAPI'
import { TOP_MODELS, modelDisplayName } from '../../config/models'
import { useToast } from '../../hooks/custom/useToast'
import {
  FILES_ONLY_PROMPT,
  addToolCall,
  applyToolResult,
  newKey,
  readConversationIdFromUrl,
  uploadErrorMessage,
  withKey,
  writeConversationIdToUrl,
} from './chatState'

// Backend accepts up to 500 messages per page
const HISTORY_PAGE_SIZE = 500

export function UnifiedChatInterface() {
  const { showToast } = useToast()

  // UI State
  const [sidebarOpen, setSidebarOpen] = useState(false)

  // Chat State
  const [inputMessage, setInputMessage] = useState('')
  // { key, file, status: 'uploading' | 'done' | 'error', progress, id, error }
  const [attachments, setAttachments] = useState([])
  const [messages, setMessages] = useState([])
  const [isSending, setIsSending] = useState(false)
  const abortRef = useRef(null)

  // Conversation State
  const [conversationId, setConversationId] = useState(null)
  const [conversations, setConversations] = useState([])

  // Model State. Fixed per conversation once it exists.
  const [selectedModel, setSelectedModel] = useState(TOP_MODELS[0].id)

  const isStarted = conversationId !== null || messages.length > 0
  const isUploading = attachments.some((a) => a.status === 'uploading')
  const readyFileIds = attachments.filter((a) => a.status === 'done').map((a) => a.id)
  const canSend = !isSending && !isUploading && (inputMessage.trim() !== '' || readyFileIds.length > 0)

  const loadConversations = useCallback(async () => {
    try {
      const data = await conversationAPI.list()
      setConversations(data)
    } catch (err) {
      showToast(`加载对话历史失败：${err.message}`)
    }
  }, [showToast])

  const loadConversation = useCallback(async (id) => {
    abortRef.current?.abort()
    try {
      const [conversation, data] = await Promise.all([
        conversationAPI.get(id),
        conversationAPI.getMessages(id, 0, HISTORY_PAGE_SIZE),
      ])
      setConversationId(id)
      setMessages(data.map(withKey))
      setSelectedModel(conversation.model_name)
      setAttachments([])
      writeConversationIdToUrl(id)
      setSidebarOpen(false)
    } catch (err) {
      showToast(`加载对话失败：${err.message}`)
      writeConversationIdToUrl(null)
    }
  }, [showToast])

  // Initial load: history list, plus the conversation named in the URL
  useEffect(() => {
    loadConversations()
    const idFromUrl = readConversationIdFromUrl()
    if (idFromUrl) {
      loadConversation(idFromUrl)
    }
    return () => abortRef.current?.abort()
  }, [loadConversations, loadConversation])

  const updateAttachment = (key, patch) => {
    setAttachments((prev) => prev.map((a) => (a.key === key ? { ...a, ...patch } : a)))
  }

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files || [])
    // Reset the input so choosing the same file again still fires onChange
    if (typeof e.target.value === 'string') {
      e.target.value = ''
    }

    files.forEach((file) => {
      const key = newKey('file')
      setAttachments((prev) => [...prev, { key, file, status: 'uploading', progress: 0 }])

      fileAPI
        .upload(file, null, (progress) => updateAttachment(key, { progress }))
        .then((info) => updateAttachment(key, { status: 'done', progress: 100, id: info.id }))
        .catch((err) => {
          const message = uploadErrorMessage(err)
          updateAttachment(key, { status: 'error', error: message })
          showToast(`${file.name} 上传失败：${message}`)
        })
    })
  }

  const removeAttachment = (key) => {
    const attachment = attachments.find((a) => a.key === key)
    setAttachments((prev) => prev.filter((a) => a.key !== key))
    // Clean up a file that was already uploaded but will not be sent
    if (attachment?.status === 'done') {
      fileAPI.delete(attachment.id).catch(() => {})
    }
  }

  const handleSendMessage = async () => {
    if (isSending) return
    if (isUploading) {
      showToast('文件还在上传，请稍候再发送', 'info')
      return
    }
    if (!canSend) return

    const messageToSend = inputMessage.trim() ? inputMessage : FILES_ONLY_PROMPT
    const fileIds = readyFileIds
    const assistantKey = newKey()
    const now = new Date().toISOString()

    setInputMessage('')
    setAttachments([])
    setMessages((prev) => [
      ...prev,
      { key: newKey(), role: 'user', content: messageToSend, created_at: now, fileCount: fileIds.length },
      { key: assistantKey, role: 'assistant', content: '', reasoning: '', tool_calls: [], created_at: now, isStreaming: true },
    ])
    setIsSending(true)

    const controller = new AbortController()
    abortRef.current = controller

    // Update the assistant message by key, never by position
    const patchAssistant = (fn) =>
      setMessages((prev) => prev.map((m) => (m.key === assistantKey ? { ...m, ...fn(m) } : m)))

    try {
      let convId = conversationId
      if (!convId) {
        const newConv = await conversationAPI.create({
          title: messageToSend.slice(0, 50),
          model_provider: 'openai',
          model_name: selectedModel,
        })
        convId = newConv.id
        setConversationId(convId)
        writeConversationIdToUrl(convId)
        loadConversations()
      }

      await chatAPI.streamChat(
        convId,
        messageToSend,
        (chunk) => patchAssistant((m) => ({ content: m.content + chunk })),
        fileIds,
        (reasoning) => patchAssistant((m) => ({ reasoning: (m.reasoning || '') + reasoning })),
        (toolCall) => patchAssistant((m) => ({ tool_calls: addToolCall(m.tool_calls, toolCall) })),
        (toolResult) => patchAssistant((m) => ({ tool_calls: applyToolResult(m.tool_calls, toolResult) })),
        { signal: controller.signal }
      )
      patchAssistant(() => ({ isStreaming: false }))
    } catch (err) {
      if (err.name === 'AbortError') {
        patchAssistant(() => ({ isStreaming: false, stopped: true }))
      } else {
        patchAssistant(() => ({
          isStreaming: false,
          isError: true,
          error: err.message || '发送失败，请稍后重试',
        }))
      }
    } finally {
      if (abortRef.current === controller) {
        abortRef.current = null
      }
      setIsSending(false)
    }
  }

  const handleStop = () => {
    abortRef.current?.abort()
  }

  const handleNewChat = () => {
    abortRef.current?.abort()
    setConversationId(null)
    setMessages([])
    setInputMessage('')
    setAttachments([])
    setSidebarOpen(false)
    writeConversationIdToUrl(null)
    // A model from an old conversation may not be offered any more
    setSelectedModel((current) =>
      TOP_MODELS.some((m) => m.id === current) ? current : TOP_MODELS[0].id
    )
  }

  const openSidebar = () => {
    setSidebarOpen(true)
    loadConversations()
  }

  const deleteConversation = async (id) => {
    try {
      await conversationAPI.delete(id)
      if (id === conversationId) {
        handleNewChat()
      }
      loadConversations()
      showToast('对话已删除', 'success')
    } catch (err) {
      showToast(`删除对话失败：${err.message}`)
    }
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
      <div className="flex-1 min-w-0 flex flex-col h-full">
        {/* Top Bar */}
        <div className="flex-shrink-0 p-2 sm:p-3 md:p-4 flex items-center justify-between bg-white/50 dark:bg-bg-secondary/50 backdrop-blur-xl border-b border-border-primary">
          <div className="flex items-center space-x-2">
            <IconButton icon={History} onClick={openSidebar} label="对话历史" />
          </div>

          <div className="flex items-center min-w-0 space-x-2 md:space-x-3">
            {isStarted && selectedModel && (
              <div
                className="min-w-0 bg-gradient-to-r from-orange-100 to-amber-100 dark:from-orange-900/30 dark:to-amber-900/30 px-3 sm:px-4 md:px-6 py-1.5 md:py-2 rounded-xl md:rounded-2xl border border-orange-300/50 dark:border-amber-400/30"
                title="当前对话使用的模型"
              >
                <div className="truncate text-xs sm:text-sm font-semibold bg-gradient-to-r from-orange-600 via-amber-600 to-rose-600 dark:from-amber-400 dark:via-orange-400 dark:to-rose-400 bg-clip-text text-transparent whitespace-nowrap">
                  {modelDisplayName(selectedModel)}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Main Chat Area - takes remaining height */}
        <div className="flex-1 overflow-hidden">
          <MainChatArea
            messages={messages}
            conversationId={conversationId}
            inputMessage={inputMessage}
            onInputChange={setInputMessage}
            onSendMessage={handleSendMessage}
            onStop={handleStop}
            isSending={isSending}
            canSend={canSend}
            attachments={attachments}
            onFileSelect={handleFileSelect}
            onRemoveAttachment={removeAttachment}
            isStarted={isStarted}
            selectedModel={selectedModel}
            onModelChange={setSelectedModel}
            modelLocked={conversationId !== null}
          />
        </div>
      </div>
    </div>
  )
}
