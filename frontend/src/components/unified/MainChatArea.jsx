import { useRef, useEffect, useState } from 'react'
import { Message } from './Message'
import { ChatInput } from './ChatInput'
import { WelcomeScreen } from './WelcomeScreen'
import { TypingIndicator } from './TypingIndicator'
import ToolCallDisplay from './ToolCallDisplay'
import { Upload } from 'lucide-react'

export function MainChatArea({
  messages = [],
  inputMessage,
  onInputChange,
  onSendMessage,
  isLoading = false,
  selectedFiles = [],
  onFileSelect,
  onRemoveFile,
  isUploading = false,
  uploadProgress = 0,
  isStarted = false,
  selectedModel,
  onModelChange,
  currentToolCalls = [],
}) {
  const messagesEndRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

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
    if (e.currentTarget === e.target) {
      setIsDragging(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      // Create a synthetic event to match the expected file input format
      const syntheticEvent = {
        target: {
          files: files
        }
      }
      onFileSelect(syntheticEvent)
    }
  }

  return (
    <div
      className="h-full flex flex-col relative"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Drag overlay */}
      {isDragging && (
        <div className="absolute inset-0 bg-orange-500/10 dark:bg-amber-500/10 backdrop-blur-sm border-4 border-dashed border-orange-400 dark:border-amber-400 rounded-2xl z-50 flex items-center justify-center animate-fadeIn">
          <div className="text-center">
            <Upload className="w-16 h-16 mx-auto mb-4 text-orange-500 dark:text-amber-400 animate-bounce" />
            <p className="text-xl font-bold text-orange-600 dark:text-amber-400">拖放文件到这里上传</p>
            <p className="text-sm text-text-secondary mt-2">支持图片、PDF、文档等格式</p>
          </div>
        </div>
      )}

      {!isStarted ? (
        // Welcome screen with centered input
        <div className="flex-1 flex items-center justify-center px-4 sm:px-6 md:px-8">
          <div className="w-full max-w-3xl">
            <WelcomeScreen />
            <ChatInput
              value={inputMessage}
              onChange={onInputChange}
              onSend={onSendMessage}
              disabled={isLoading}
              selectedFiles={selectedFiles}
              onFileSelect={onFileSelect}
              onRemoveFile={onRemoveFile}
              isUploading={isUploading}
              uploadProgress={uploadProgress}
              selectedModel={selectedModel}
              onModelChange={onModelChange}
            />
          </div>
        </div>
      ) : (
        <>
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-3 sm:px-4 md:px-6 lg:px-8 py-4 md:py-6">
            <div className="max-w-4xl mx-auto space-y-4 md:space-y-6">
              {messages.map((msg, index) => (
                <Message key={msg.id || index} message={msg} index={index} />
              ))}

              {/* Show current tool calls if loading and there are tool calls */}
              {isLoading && currentToolCalls.length > 0 && (
                <div className="flex justify-start animate-fadeIn">
                  <div className="max-w-3xl break-words bg-message-assistant backdrop-blur-xl border border-border-primary rounded-2xl md:rounded-[2rem] px-4 sm:px-6 md:px-8 py-4 sm:py-5 md:py-6 shadow-lg">
                    <ToolCallDisplay toolCalls={currentToolCalls} />
                  </div>
                </div>
              )}

              {isLoading && <TypingIndicator />}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area - Fixed at bottom */}
          <div className="flex-shrink-0 px-3 sm:px-4 md:px-6 lg:px-8 py-3 md:py-4 lg:py-6 bg-bg-secondary/50 dark:bg-bg-secondary/30 border-t border-border-primary">
            <div className="max-w-4xl mx-auto">
              <ChatInput
                value={inputMessage}
                onChange={onInputChange}
                onSend={onSendMessage}
                disabled={isLoading}
                selectedFiles={selectedFiles}
                onFileSelect={onFileSelect}
                onRemoveFile={onRemoveFile}
                isUploading={isUploading}
                uploadProgress={uploadProgress}
                selectedModel={selectedModel}
                onModelChange={onModelChange}
              />
            </div>
          </div>
        </>
      )}
    </div>
  )
}
