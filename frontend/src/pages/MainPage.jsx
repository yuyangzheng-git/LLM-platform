import { useState, useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  Send,
  Paperclip,
  Mic,
  Settings,
  History,
  Plus,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  Download,
  X,
  Menu,
  ChevronDown,
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { conversationAPI } from '../services/conversationAPI'
import { fileAPI } from '../services/fileAPI'
import { modelAPI } from '../services/modelAPI'
import { chatAPI } from '../services/chatAPI'

// Markdown components
const markdownComponents = {
  code({ node, inline, className, children, ...props }) {
    const match = /language-(\w+)/.exec(className || '')
    const language = match ? match[1] : ''
    return !inline && language ? (
      <div className="relative group my-4">
        <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => navigator.clipboard.writeText(String(children))}
            className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white text-xs rounded flex items-center space-x-1"
          >
            <Copy className="w-3 h-3" />
            <span>Copy</span>
          </button>
        </div>
        <SyntaxHighlighter style={oneDark} language={language} PreTag="div" {...props}>
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      </div>
    ) : (
      <code className="bg-gray-100 text-gray-900 px-1.5 py-0.5 rounded text-sm font-mono" {...props}>
        {children}
      </code>
    )
  },
  p({ children }) {
    return <p className="mb-4 last:mb-0 leading-relaxed">{children}</p>
  },
  ul({ children }) {
    return <ul className="list-disc list-inside mb-4 space-y-2">{children}</ul>
  },
  ol({ children }) {
    return <ol className="list-decimal list-inside mb-4 space-y-2">{children}</ol>
  },
  blockquote({ children }) {
    return <blockquote className="border-l-4 border-blue-500 pl-4 py-2 my-4 bg-blue-50">{children}</blockquote>
  },
  h1({ children }) {
    return <h1 className="text-3xl font-bold mb-4 mt-6 first:mt-0">{children}</h1>
  },
  h2({ children }) {
    return <h2 className="text-2xl font-bold mb-3 mt-5 first:mt-0">{children}</h2>
  },
  h3({ children }) {
    return <h3 className="text-xl font-bold mb-3 mt-4 first:mt-0">{children}</h3>
  },
}

function MainPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  // State
  const [isStarted, setIsStarted] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [currentView, setCurrentView] = useState('chat') // 'chat', 'history', 'settings'
  const [inputMessage, setInputMessage] = useState('')
  const [selectedFiles, setSelectedFiles] = useState([])
  const [uploadedFileIds, setUploadedFileIds] = useState([])
  const [isUploading, setIsUploading] = useState(false)
  const [conversationId, setConversationId] = useState(null)
  const [conversations, setConversations] = useState([])
  const [providers, setProviders] = useState([])
  const [selectedProvider, setSelectedProvider] = useState('')
  const [selectedModel, setSelectedModel] = useState('')
  const [availableModels, setAvailableModels] = useState([])
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const fileInputRef = useRef(null)
  const textareaRef = useRef(null)
  const messagesEndRef = useRef(null)

  // Load initial data
  useEffect(() => {
    loadProviders()
    loadConversations()
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
    }
  }, [inputMessage])

  const loadProviders = async () => {
    try {
      const data = await modelAPI.getProviders()
      setProviders(data)
      if (data.length > 0) {
        setSelectedProvider(data[0].provider)
        setAvailableModels(data[0].available_models || [])
        if (data[0].available_models?.length > 0) {
          setSelectedModel(data[0].available_models[0])
        }
      }
    } catch (err) {
      console.error('Failed to load providers:', err)
    }
  }

  const loadConversations = async () => {
    try {
      const data = await conversationAPI.list()
      setConversations(data)
    } catch (err) {
      console.error('Failed to load conversations:', err)
    }
  }

  const handleProviderChange = (provider) => {
    setSelectedProvider(provider)
    const providerData = providers.find(p => p.provider === provider)
    if (providerData) {
      setAvailableModels(providerData.available_models || [])
      if (providerData.available_models?.length > 0) {
        setSelectedModel(providerData.available_models[0])
      }
    }
  }

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files)
    setSelectedFiles(prev => [...prev, ...files])

    setIsUploading(true)
    try {
      const uploadedFiles = await fileAPI.uploadBatch(files)
      const fileIds = uploadedFiles.map(f => f.id)
      setUploadedFileIds(prev => [...prev, ...fileIds])
    } catch (err) {
      console.error('File upload failed:', err)
    } finally {
      setIsUploading(false)
    }
  }

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index))
    setUploadedFileIds(prev => prev.filter((_, i) => i !== index))
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() && uploadedFileIds.length === 0) return

    const messageToSend = inputMessage
    const filesToSend = uploadedFileIds

    // Clear input immediately
    setInputMessage('')
    setSelectedFiles([])
    setUploadedFileIds([])
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }

    // Start conversation if not started
    if (!isStarted) {
      setIsStarted(true)
    }

    // Add user message immediately
    const userMessage = {
      role: 'user',
      content: messageToSend,
      created_at: new Date().toISOString(),
    }
    setMessages(prev => [...prev, userMessage])

    // Create new conversation if needed
    let convId = conversationId
    if (!convId) {
      try {
        const newConv = await conversationAPI.create({
          title: messageToSend.slice(0, 50),
          model_provider: selectedProvider,
          model_name: selectedModel,
        })
        convId = newConv.id
        setConversationId(convId)
        loadConversations()
      } catch (err) {
        console.error('Failed to create conversation:', err)
        return
      }
    }

    // Send message with streaming
    try {
      let fullResponse = ''
      await chatAPI.streamChat(
        convId,
        messageToSend,
        (chunk) => {
          fullResponse += chunk
          setMessages(prev => {
            const newMessages = [...prev]
            const lastMsg = newMessages[newMessages.length - 1]
            if (lastMsg && lastMsg.role === 'assistant' && !lastMsg.id) {
              lastMsg.content = fullResponse
            } else {
              newMessages.push({
                role: 'assistant',
                content: fullResponse,
                created_at: new Date().toISOString(),
              })
            }
            return newMessages
          })
        },
        filesToSend
      )
    } catch (err) {
      console.error('Failed to send message:', err)
    }
  }

  const handleNewChat = () => {
    setConversationId(null)
    setMessages([])
    setIsStarted(false)
    setInputMessage('')
    setSelectedFiles([])
    setUploadedFileIds([])
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

  const exportConversation = async (format) => {
    if (!conversationId || messages.length === 0) return

    const content = messages.map(m => `${m.role.toUpperCase()}:\n${m.content}\n\n`).join('')
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `conversation-${conversationId}.${format}`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -right-1/2 w-full h-full bg-gradient-to-br from-blue-400/10 to-purple-400/10 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute -bottom-1/2 -left-1/2 w-full h-full bg-gradient-to-tr from-indigo-400/10 to-pink-400/10 rounded-full blur-3xl animate-pulse-slow delay-1000"></div>
      </div>

      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'w-80' : 'w-0'
        } transition-all duration-300 bg-white/80 backdrop-blur-xl border-r border-gray-200/50 overflow-hidden flex flex-col relative z-20 shadow-2xl`}
      >
        {sidebarOpen && (
          <>
            {/* Sidebar Header */}
            <div className="p-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-lg font-bold text-gray-900">
                {currentView === 'history' && 'Chat History'}
                {currentView === 'settings' && 'Settings'}
              </h2>
              <button
                onClick={() => setSidebarOpen(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Sidebar Content */}
            <div className="flex-1 overflow-y-auto p-4">
              {currentView === 'history' && (
                <div className="space-y-2">
                  <button
                    onClick={handleNewChat}
                    className="w-full flex items-center space-x-3 px-6 py-4 bg-gradient-to-br from-blue-600 via-blue-500 to-purple-600 text-white rounded-2xl hover:from-blue-700 hover:to-purple-700 transition-all shadow-xl hover:shadow-2xl hover:scale-[1.02]"
                  >
                    <Plus className="w-5 h-5" />
                    <span className="font-semibold">New Chat</span>
                  </button>

                  {conversations.map(conv => (
                    <button
                      key={conv.id}
                      onClick={() => loadConversation(conv.id)}
                      className={`w-full text-left px-5 py-4 rounded-2xl transition-all ${
                        conv.id === conversationId
                          ? 'bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-300 shadow-lg'
                          : 'hover:bg-gray-50 border-2 border-transparent hover:shadow-md'
                      }`}
                    >
                      <div className="font-medium text-gray-900 truncate">{conv.title}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        {conv.model_provider} • {new Date(conv.created_at).toLocaleDateString()}
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {currentView === 'settings' && (
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Model Provider
                    </label>
                    <select
                      value={selectedProvider}
                      onChange={(e) => handleProviderChange(e.target.value)}
                      className="w-full px-5 py-3 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white hover:border-gray-300 transition-all shadow-sm font-medium"
                    >
                      {providers.map(p => (
                        <option key={p.provider} value={p.provider}>
                          {p.provider}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Model
                    </label>
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className="w-full px-5 py-3 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white hover:border-gray-300 transition-all shadow-sm font-medium"
                    >
                      {availableModels.map(model => (
                        <option key={model} value={model}>
                          {model}
                        </option>
                      ))}
                    </select>
                  </div>

                  {isStarted && messages.length > 0 && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Export Conversation
                      </label>
                      <div className="space-y-2">
                        <button
                          onClick={() => exportConversation('txt')}
                          className="w-full px-5 py-3 bg-gradient-to-r from-gray-50 to-gray-100 hover:from-gray-100 hover:to-gray-200 rounded-2xl transition-all text-sm font-semibold shadow-sm hover:shadow-md border border-gray-200"
                        >
                          📄 Export as TXT
                        </button>
                        <button
                          onClick={() => exportConversation('md')}
                          className="w-full px-5 py-3 bg-gradient-to-r from-gray-50 to-gray-100 hover:from-gray-100 hover:to-gray-200 rounded-2xl transition-all text-sm font-semibold shadow-sm hover:shadow-md border border-gray-200"
                        >
                          📝 Export as Markdown
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col relative z-10">
        {/* Top Bar */}
        <div className="absolute top-0 left-0 right-0 z-10 p-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => {
                setSidebarOpen(true)
                setCurrentView('history')
              }}
              className="p-2.5 hover:bg-white/90 rounded-xl transition-all backdrop-blur-md bg-white/70 shadow-lg hover:shadow-xl border border-white/50"
            >
              <Menu className="w-5 h-5 text-gray-700" />
            </button>
            <button
              onClick={() => {
                setSidebarOpen(true)
                setCurrentView('settings')
              }}
              className="p-2.5 hover:bg-white/90 rounded-xl transition-all backdrop-blur-md bg-white/70 shadow-lg hover:shadow-xl border border-white/50"
            >
              <Settings className="w-5 h-5 text-gray-700" />
            </button>
          </div>

          {isStarted && (
            <div className="bg-white/70 backdrop-blur-xl px-6 py-3 rounded-2xl shadow-lg border border-white/50">
              <div className="text-sm font-medium bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {selectedProvider} • {selectedModel}
              </div>
            </div>
          )}
        </div>

        {/* Messages Area */}
        <div
          className={`flex-1 overflow-y-auto transition-all duration-700 ${
            isStarted ? 'pt-20 pb-6' : 'pt-0 pb-0'
          }`}
        >
          {isStarted ? (
            <div className="max-w-4xl mx-auto px-8 space-y-6">
              {messages.map((msg, index) => (
                <div
                  key={msg.id || index}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <div
                    className={`max-w-3xl ${
                      msg.role === 'user'
                        ? 'bg-gradient-to-br from-blue-600 via-blue-500 to-purple-600 text-white rounded-[2rem] px-8 py-5 shadow-xl hover:shadow-2xl transition-all'
                        : 'bg-white/90 backdrop-blur-xl border border-gray-200/50 rounded-[2rem] px-8 py-6 shadow-lg hover:shadow-xl transition-all'
                    }`}
                  >
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                      {msg.content}
                    </ReactMarkdown>

                    {msg.role === 'assistant' && (
                      <div className="flex items-center space-x-2 mt-4 pt-3 border-t border-gray-100">
                        <button
                          onClick={() => navigator.clipboard.writeText(msg.content)}
                          className="p-1.5 hover:bg-gray-100 rounded transition-colors"
                          title="Copy"
                        >
                          <Copy className="w-4 h-4 text-gray-600" />
                        </button>
                        <button className="p-1.5 hover:bg-gray-100 rounded transition-colors">
                          <ThumbsUp className="w-4 h-4 text-gray-600" />
                        </button>
                        <button className="p-1.5 hover:bg-gray-100 rounded transition-colors">
                          <ThumbsDown className="w-4 h-4 text-gray-600" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-2xl">
                  {error}
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          ) : null}
        </div>

        {/* Input Area - Center or Bottom */}
        <div
          className={`transition-all duration-700 ${
            isStarted
              ? 'relative px-8 py-6 bg-white border-t border-gray-200'
              : 'absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full max-w-3xl px-8'
          }`}
        >
          {!isStarted && (
            <div className="text-center mb-12 animate-fadeIn">
              <div className="relative inline-block mb-6">
                <h1 className="text-8xl font-black bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent animate-pulse-slow">
                  KIMI
                </h1>
                <div className="absolute -inset-4 bg-gradient-to-r from-blue-400/20 via-purple-400/20 to-pink-400/20 blur-2xl -z-10"></div>
              </div>
              <p className="text-gray-600 text-xl font-medium">What can I help you with today?</p>
              <p className="text-gray-400 text-sm mt-2">Powered by advanced AI models</p>
            </div>
          )}

          <div className={isStarted ? 'max-w-4xl mx-auto' : ''}>
            {selectedFiles.length > 0 && (
              <div className="mb-4 flex flex-wrap gap-3 animate-slideUp">
                {selectedFiles.map((file, index) => (
                  <div
                    key={index}
                    className="group bg-gradient-to-r from-blue-500/10 to-purple-500/10 backdrop-blur-sm border border-blue-200 text-blue-700 px-5 py-3 rounded-2xl text-sm font-medium flex items-center space-x-3 hover:shadow-lg transition-all"
                  >
                    <Paperclip className="w-4 h-4" />
                    <span className="max-w-[200px] truncate">{file.name}</span>
                    <button
                      onClick={() => removeFile(index)}
                      className="p-1 hover:bg-red-100 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <X className="w-4 h-4 text-red-600" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="flex items-end space-x-3 bg-white/90 backdrop-blur-xl rounded-[2rem] p-5 border-2 border-gray-200/50 focus-within:border-blue-400 focus-within:shadow-2xl transition-all shadow-xl hover:shadow-2xl">
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={isLoading || isUploading}
                className="p-2.5 text-gray-600 hover:bg-gradient-to-r hover:from-blue-500 hover:to-purple-500 hover:text-white rounded-xl transition-all flex-shrink-0"
              >
                <Paperclip className="w-5 h-5" />
              </button>

              <input
                ref={fileInputRef}
                type="file"
                multiple
                onChange={handleFileSelect}
                className="hidden"
                accept="image/*,.pdf,.txt,.md,.doc,.docx,.csv,.xlsx"
              />

              <textarea
                ref={textareaRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSendMessage()
                  }
                }}
                placeholder="Type your message..."
                disabled={isLoading}
                className="flex-1 bg-transparent border-none outline-none resize-none placeholder-gray-400 text-gray-900 max-h-40 text-lg font-medium"
                rows={1}
              />

              <button
                onClick={handleSendMessage}
                disabled={isLoading || (!inputMessage.trim() && uploadedFileIds.length === 0)}
                className="w-14 h-14 bg-gradient-to-br from-blue-600 via-blue-500 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-300 disabled:to-gray-300 text-white rounded-2xl flex items-center justify-center transition-all shadow-xl hover:shadow-2xl hover:scale-105 disabled:shadow-none disabled:scale-100 flex-shrink-0"
              >
                <Send className="w-6 h-6" />
              </button>
            </div>

            <p className="text-xs text-gray-400 mt-4 text-center font-medium">
              Press <kbd className="px-2 py-1 bg-gray-200 rounded text-gray-700">Enter</kbd> to send • <kbd className="px-2 py-1 bg-gray-200 rounded text-gray-700">Shift + Enter</kbd> for new line
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MainPage
