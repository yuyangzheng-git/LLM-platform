import { useRef, useEffect, useState } from 'react'
import { Send, Paperclip, X, Sparkles } from 'lucide-react'
import { TOP_MODELS } from '../../config/models'

export function ChatInput({
  value,
  onChange,
  onSend,
  disabled = false,
  selectedFiles = [],
  onFileSelect,
  onRemoveFile,
  isUploading = false,
  uploadProgress = 0,
  selectedModel = 'gpt-4o',
  onModelChange,
}) {
  const textareaRef = useRef(null)
  const fileInputRef = useRef(null)
  const [isComposing, setIsComposing] = useState(false)

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
    }
  }, [value])

  const handleKeyDown = (e) => {
    // 防止中文输入法输入时误触发发送
    if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
      e.preventDefault()
      onSend()
    }
  }

  const handleCompositionStart = () => {
    setIsComposing(true)
  }

  const handleCompositionEnd = () => {
    setIsComposing(false)
  }

  const handleFileClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div>
      {selectedFiles.length > 0 && (
        <div className="mb-3 md:mb-4 max-h-32 overflow-y-auto flex flex-wrap gap-2 md:gap-3 animate-slideUp">
          {selectedFiles.map((file, index) => (
            <div
              key={index}
              className="group relative bg-orange-500/10 dark:bg-amber-500/10 backdrop-blur-sm border-2 border-orange-200 dark:border-amber-400/50 text-orange-700 dark:text-amber-300 px-3 sm:px-4 md:px-5 py-3 md:py-4 rounded-xl md:rounded-2xl text-xs sm:text-sm font-medium flex flex-col hover:shadow-lg transition-all flex-shrink-0 min-w-[200px]"
            >
              {/* 文件名和图标 */}
              <div className="relative z-10 flex items-center justify-between w-full mb-2">
                <div className="flex items-center space-x-2">
                  <Paperclip className="w-4 h-4 flex-shrink-0" />
                  <span className="max-w-[150px] truncate font-semibold">{file.name}</span>
                </div>

                {/* 删除按钮 */}
                {!isUploading && (
                  <button
                    onClick={() => onRemoveFile(index)}
                    className="p-1 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-colors flex-shrink-0"
                  >
                    <X className="w-4 h-4 text-red-600 dark:text-red-400" />
                  </button>
                )}
              </div>

              {/* 上传进度条 */}
              {isUploading && (
                <div className="relative z-10 w-full">
                  {/* 进度条背景 */}
                  <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-orange-500 to-amber-500 dark:from-orange-600 dark:to-amber-600 transition-all duration-300 ease-out"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                  {/* 百分比文字 */}
                  <div className="flex justify-between items-center mt-1">
                    <span className="text-xs text-orange-600 dark:text-amber-400">上传中...</span>
                    <span className="text-xs font-bold text-orange-600 dark:text-amber-400">
                      {uploadProgress}%
                    </span>
                  </div>
                </div>
              )}

              {/* 上传完成提示 */}
              {!isUploading && (
                <div className="text-xs text-green-600 dark:text-green-400 flex items-center space-x-1">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>已上传</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="flex items-center space-x-2 md:space-x-3 bg-white/90 dark:bg-bg-secondary/90 backdrop-blur-xl rounded-2xl md:rounded-[2rem] p-2 sm:p-3 md:p-4 border-2 border-border-primary focus-within:border-orange-400 dark:focus-within:border-amber-400 focus-within:shadow-2xl transition-all shadow-xl hover:shadow-2xl">
        <button
          onClick={handleFileClick}
          disabled={disabled || isUploading}
          className="p-1.5 md:p-2 text-text-secondary hover:bg-gradient-main hover:text-white rounded-lg md:rounded-xl transition-all flex-shrink-0"
          title="上传文件"
        >
          <Paperclip className="w-4 h-4 md:w-5 md:h-5" />
        </button>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={onFileSelect}
          className="hidden"
          accept="image/*,.pdf,.txt,.md,.doc,.docx,.csv,.xlsx"
        />

        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onCompositionStart={handleCompositionStart}
          onCompositionEnd={handleCompositionEnd}
          placeholder="输入消息..."
          disabled={disabled}
          className="flex-1 bg-transparent border-none outline-none resize-none placeholder-text-tertiary text-text-primary max-h-40 text-sm sm:text-base font-medium py-1"
          rows={1}
        />

        {/* Model Selector */}
        <div className="relative group flex-shrink-0">
          <select
            value={selectedModel}
            onChange={(e) => onModelChange && onModelChange(e.target.value)}
            className="appearance-none bg-gradient-to-r from-orange-100 to-amber-100 dark:from-orange-900/30 dark:to-amber-900/30 text-text-primary px-2 sm:px-3 py-1.5 sm:py-2 pr-6 sm:pr-8 rounded-lg md:rounded-xl text-xs sm:text-sm font-medium border border-orange-300/50 dark:border-amber-400/30 hover:shadow-lg transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-orange-400 dark:focus:ring-amber-400"
            title="选择模型"
          >
            {TOP_MODELS.map((model) => (
              <option key={model.id} value={model.id}>
                {model.name}
              </option>
            ))}
          </select>
          <Sparkles className="w-3 h-3 md:w-4 md:h-4 absolute right-1.5 sm:right-2 top-1/2 -translate-y-1/2 text-orange-500 dark:text-amber-400 pointer-events-none" />
        </div>

        <button
          onClick={onSend}
          disabled={disabled || (!value.trim() && selectedFiles.length === 0)}
          className="w-8 h-8 sm:w-9 sm:h-9 md:w-10 md:h-10 bg-gradient-main hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg md:rounded-xl flex items-center justify-center transition-all shadow-lg hover:shadow-xl hover:scale-105 disabled:shadow-none disabled:scale-100 flex-shrink-0"
          title="发送消息 (Enter)"
        >
          <Send className="w-4 h-4 md:w-5 md:h-5" />
        </button>
      </div>

      <p className="text-xs text-text-tertiary mt-3 md:mt-4 text-center font-medium">
        Press <kbd className="px-1.5 md:px-2 py-0.5 md:py-1 bg-bg-tertiary rounded text-text-secondary text-xs">Enter</kbd> to send •{' '}
        <kbd className="px-1.5 md:px-2 py-0.5 md:py-1 bg-bg-tertiary rounded text-text-secondary text-xs">Shift + Enter</kbd> for new line
      </p>
    </div>
  )
}
