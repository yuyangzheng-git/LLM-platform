import { useRef, useLayoutEffect, useState } from 'react'
import { Message } from './Message'
import { ChatInput } from './ChatInput'
import { WelcomeScreen } from './WelcomeScreen'
import { ArrowDown, Upload } from 'lucide-react'

// How close to the bottom (px) still counts as "following" new output
const STICK_THRESHOLD = 80

export function MainChatArea({
  messages = [],
  conversationId,
  inputMessage,
  onInputChange,
  onSendMessage,
  onStop,
  isSending = false,
  canSend = false,
  attachments = [],
  onFileSelect,
  onRemoveAttachment,
  isStarted = false,
  selectedModel,
  onModelChange,
  modelLocked = false,
}) {
  const scrollRef = useRef(null)
  const stickToBottomRef = useRef(true)
  const [showJumpToLatest, setShowJumpToLatest] = useState(false)
  const [isDragging, setIsDragging] = useState(false)

  const lastConversationRef = useRef(conversationId)

  // Follow new output only while the user is at the bottom; scrolling up
  // to read earlier messages is never interrupted. Opening another
  // conversation always starts at its latest message.
  useLayoutEffect(() => {
    if (lastConversationRef.current !== conversationId) {
      lastConversationRef.current = conversationId
      stickToBottomRef.current = true
      setShowJumpToLatest(false)
    }
    const el = scrollRef.current
    if (el && stickToBottomRef.current) {
      el.scrollTop = el.scrollHeight
    }
  }, [messages, isStarted, conversationId])

  const handleScroll = () => {
    const el = scrollRef.current
    if (!el) return
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < STICK_THRESHOLD
    stickToBottomRef.current = atBottom
    setShowJumpToLatest(!atBottom)
  }

  const jumpToLatest = () => {
    const el = scrollRef.current
    if (!el) return
    stickToBottomRef.current = true
    setShowJumpToLatest(false)
    el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  }

  const handleSend = () => {
    // Sending always brings the new exchange into view
    stickToBottomRef.current = true
    onSendMessage()
  }

  // Drag and drop handlers
  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    // Only set to false if we're leaving the main container
    if (!e.currentTarget.contains(e.relatedTarget)) {
      setIsDragging(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      onFileSelect({ target: { files } })
    }
  }

  const chatInput = (
    <ChatInput
      value={inputMessage}
      onChange={onInputChange}
      onSend={handleSend}
      onStop={onStop}
      isSending={isSending}
      canSend={canSend}
      attachments={attachments}
      onFileSelect={onFileSelect}
      onRemoveAttachment={onRemoveAttachment}
      selectedModel={selectedModel}
      onModelChange={onModelChange}
      modelLocked={modelLocked}
    />
  )

  return (
    <div
      className="h-full flex flex-col relative"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Drag overlay */}
      {isDragging && (
        <div className="absolute inset-0 bg-roots-500/10 dark:bg-road-500/10 backdrop-blur-sm border-4 border-dashed border-roots-400 dark:border-road-400 rounded-2xl z-50 flex items-center justify-center animate-fadeIn pointer-events-none">
          <div className="text-center">
            <Upload className="w-16 h-16 mx-auto mb-4 text-roots-500 dark:text-road-400 animate-bounce" />
            <p className="text-xl font-bold text-roots-600 dark:text-road-400">拖放文件到这里上传</p>
            <p className="text-sm text-text-secondary mt-2">支持图片、PDF、文档等格式</p>
          </div>
        </div>
      )}

      {!isStarted ? (
        // Welcome screen with centered input
        <div className="scroll-area flex-1 min-h-0 overflow-y-auto flex px-3 sm:px-6 md:px-8 pb-[max(0.75rem,env(safe-area-inset-bottom))]">
          <div className="w-full max-w-3xl m-auto py-4">
            <WelcomeScreen />
            {chatInput}
          </div>
        </div>
      ) : (
        <>
          {/* Messages Area */}
          <div
            ref={scrollRef}
            onScroll={handleScroll}
            className="scroll-area flex-1 min-h-0 overflow-y-auto px-3 sm:px-4 md:px-6 lg:px-8 py-3 md:py-6"
          >
            <div className="max-w-4xl mx-auto space-y-4 md:space-y-6">
              {messages.map((msg) => (
                <Message key={msg.key} message={msg} />
              ))}
            </div>
          </div>

          {showJumpToLatest && (
            <div className="relative">
              <button
                onClick={jumpToLatest}
                className="absolute left-1/2 -translate-x-1/2 -top-14 z-10 flex items-center gap-1.5 px-3 py-2 rounded-full bg-cream/90 dark:bg-bg-secondary/90 border border-border-primary shadow-lg text-sm text-text-primary hover:shadow-xl animate-fadeIn"
              >
                <ArrowDown className="w-4 h-4" />
                <span>回到最新</span>
              </button>
            </div>
          )}

          {/* Input Area - Fixed at bottom */}
          <div className="flex-shrink-0 px-2 sm:px-4 md:px-6 lg:px-8 pt-2 pb-[max(0.75rem,env(safe-area-inset-bottom))] md:pb-6 [@media(max-height:500px)]:pb-[max(0.5rem,env(safe-area-inset-bottom))]">
            <div className="max-w-4xl mx-auto">{chatInput}</div>
          </div>
        </>
      )}
    </div>
  )
}
