import { useRef, useEffect, useState } from 'react'
import { Send, Paperclip, X, Sparkles, Square, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'
import { TOP_MODELS } from '../../config/models'
import { isImeEnter } from './chatState'

// On touch keyboards Enter inserts a newline; sending is done with the button
const isTouchDevice = () =>
  typeof window !== 'undefined' && window.matchMedia?.('(pointer: coarse)').matches

function AttachmentChip({ attachment, onRemove }) {
  const { file, status, progress, error } = attachment
  return (
    <div
      className={`relative bg-orange-500/10 dark:bg-amber-500/10 backdrop-blur-sm border-2 px-3 py-2 rounded-xl text-xs sm:text-sm font-medium flex flex-col flex-shrink-0 w-[200px] max-w-full ${
        status === 'error'
          ? 'border-red-300 dark:border-red-500/50 text-red-700 dark:text-red-300'
          : 'border-orange-200 dark:border-amber-400/50 text-orange-700 dark:text-amber-300'
      }`}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <Paperclip className="w-4 h-4 flex-shrink-0" />
          <span className="truncate font-semibold" title={file.name}>{file.name}</span>
        </div>
        <button
          onClick={onRemove}
          className="p-1 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-colors flex-shrink-0"
          aria-label={`移除 ${file.name}`}
        >
          <X className="w-4 h-4 text-red-600 dark:text-red-400" />
        </button>
      </div>

      {status === 'uploading' && (
        <div className="mt-1.5">
          <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-orange-500 to-amber-500 transition-all duration-300 ease-out"
              style={{ width: `${progress || 0}%` }}
            />
          </div>
          <div className="flex items-center gap-1 mt-1 text-xs">
            <Loader2 className="w-3 h-3 animate-spin" />
            <span>上传中 {progress || 0}%</span>
          </div>
        </div>
      )}
      {status === 'done' && (
        <div className="mt-1 flex items-center gap-1 text-xs text-green-600 dark:text-green-400">
          <CheckCircle2 className="w-3 h-3" />
          <span>已上传</span>
        </div>
      )}
      {status === 'error' && (
        <div className="mt-1 flex items-start gap-1 text-xs" title={error}>
          <AlertCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
          <span className="line-clamp-2">上传失败，不会随消息发送</span>
        </div>
      )}
    </div>
  )
}

export function ChatInput({
  value,
  onChange,
  onSend,
  onStop,
  isSending = false,
  canSend = false,
  attachments = [],
  onFileSelect,
  onRemoveAttachment,
  selectedModel = TOP_MODELS[0].id,
  onModelChange,
  modelLocked = false,
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
    if (e.key !== 'Enter' || e.shiftKey || isImeEnter(e, isComposing) || isTouchDevice()) {
      return
    }
    e.preventDefault()
    if (canSend) {
      onSend()
    }
  }

  // Keep the current model selectable even if it is not in the preset list
  // (e.g. a conversation created with another model)
  const modelOptions = TOP_MODELS.some((m) => m.id === selectedModel)
    ? TOP_MODELS
    : [{ id: selectedModel, name: selectedModel }, ...TOP_MODELS]

  return (
    <div>
      {attachments.length > 0 && (
        <div className="mb-3 md:mb-4 max-h-32 overflow-y-auto flex flex-wrap gap-2 md:gap-3 animate-slideUp">
          {attachments.map((attachment) => (
            <AttachmentChip
              key={attachment.key}
              attachment={attachment}
              onRemove={() => onRemoveAttachment(attachment.key)}
            />
          ))}
        </div>
      )}

      <div className="flex items-center gap-1.5 sm:gap-2 md:gap-3 bg-white/90 dark:bg-bg-secondary/90 backdrop-blur-xl rounded-2xl md:rounded-[2rem] p-2 sm:p-3 md:p-4 border-2 border-border-primary focus-within:border-orange-400 dark:focus-within:border-amber-400 focus-within:shadow-2xl transition-all shadow-xl hover:shadow-2xl">
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isSending}
          className="p-1.5 md:p-2 text-text-secondary hover:bg-gradient-main hover:text-white rounded-lg md:rounded-xl transition-all flex-shrink-0 disabled:opacity-50"
          title="上传文件"
          aria-label="上传文件"
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
          onCompositionStart={() => setIsComposing(true)}
          onCompositionEnd={() => setIsComposing(false)}
          placeholder="输入消息..."
          aria-label="输入消息"
          className="flex-1 min-w-0 bg-transparent border-none outline-none resize-none placeholder-text-tertiary text-text-primary max-h-40 text-sm sm:text-base font-medium py-1"
          rows={1}
        />

        {/* Model Selector: fixed once the conversation exists */}
        <div className="relative flex-shrink-0 max-w-[6.5rem] sm:max-w-none">
          <select
            value={selectedModel}
            onChange={(e) => onModelChange && onModelChange(e.target.value)}
            disabled={modelLocked}
            className="w-full appearance-none truncate bg-gradient-to-r from-orange-100 to-amber-100 dark:from-orange-900/30 dark:to-amber-900/30 text-text-primary px-2 sm:px-3 py-1.5 sm:py-2 pr-6 sm:pr-8 rounded-lg md:rounded-xl text-xs sm:text-sm font-medium border border-orange-300/50 dark:border-amber-400/30 hover:shadow-lg transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-orange-400 dark:focus:ring-amber-400 disabled:cursor-not-allowed disabled:opacity-70 disabled:hover:shadow-none"
            title={modelLocked ? '对话的模型已固定，新建对话可切换模型' : '选择模型'}
            aria-label="选择模型"
          >
            {modelOptions.map((model) => (
              <option key={model.id} value={model.id}>
                {model.name}
              </option>
            ))}
          </select>
          <Sparkles className="w-3 h-3 md:w-4 md:h-4 absolute right-1.5 sm:right-2 top-1/2 -translate-y-1/2 text-orange-500 dark:text-amber-400 pointer-events-none" />
        </div>

        {isSending ? (
          <button
            onClick={onStop}
            className="w-8 h-8 sm:w-9 sm:h-9 md:w-10 md:h-10 bg-stone-700 hover:bg-stone-800 dark:bg-stone-200 dark:hover:bg-white text-white dark:text-stone-900 rounded-lg md:rounded-xl flex items-center justify-center transition-all shadow-lg flex-shrink-0"
            title="停止生成"
            aria-label="停止生成"
          >
            <Square className="w-3.5 h-3.5 md:w-4 md:h-4" fill="currentColor" />
          </button>
        ) : (
          <button
            onClick={onSend}
            disabled={!canSend}
            className="w-8 h-8 sm:w-9 sm:h-9 md:w-10 md:h-10 bg-gradient-main hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg md:rounded-xl flex items-center justify-center transition-all shadow-lg hover:shadow-xl hover:scale-105 disabled:shadow-none disabled:scale-100 flex-shrink-0"
            title="发送消息 (Enter)"
            aria-label="发送消息"
          >
            <Send className="w-4 h-4 md:w-5 md:h-5" />
          </button>
        )}
      </div>

      <p className="hidden md:block text-xs text-text-tertiary mt-3 md:mt-4 text-center font-medium">
        按 <kbd className="px-1.5 md:px-2 py-0.5 md:py-1 bg-bg-tertiary rounded text-text-secondary text-xs">Enter</kbd> 发送，
        <kbd className="px-1.5 md:px-2 py-0.5 md:py-1 bg-bg-tertiary rounded text-text-secondary text-xs">Shift + Enter</kbd> 换行
      </p>
    </div>
  )
}
