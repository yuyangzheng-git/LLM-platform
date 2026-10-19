import { useEffect, useRef, useState } from 'react'
import { Plus, X, Trash2 } from 'lucide-react'
import { modelDisplayName } from '../../config/models'

export function ConversationSidebar({
  isOpen,
  onClose,
  conversations = [],
  currentConversationId,
  onSelectConversation,
  onDeleteConversation,
  onNewChat,
}) {
  // Conversation id waiting for delete confirmation
  const [confirmingId, setConfirmingId] = useState(null)
  const closeButtonRef = useRef(null)
  const touchStartRef = useRef(null)
  // How far the drawer is being dragged left (px), for swipe-to-close
  const [dragX, setDragX] = useState(0)

  useEffect(() => {
    if (!isOpen) return undefined
    closeButtonRef.current?.focus({ preventScroll: true })
    const onKeyDown = (e) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [isOpen, onClose])

  if (!isOpen) return null

  // Swipe left to close (phones); vertical scrolling is left alone
  const handleTouchStart = (e) => {
    const touch = e.touches[0]
    touchStartRef.current = { x: touch.clientX, y: touch.clientY, horizontal: null }
  }

  const handleTouchMove = (e) => {
    const start = touchStartRef.current
    if (!start) return
    const touch = e.touches[0]
    const dx = touch.clientX - start.x
    const dy = touch.clientY - start.y
    if (start.horizontal === null && (Math.abs(dx) > 8 || Math.abs(dy) > 8)) {
      start.horizontal = Math.abs(dx) > Math.abs(dy)
    }
    if (start.horizontal) {
      setDragX(Math.min(0, dx))
    }
  }

  const handleTouchEnd = () => {
    const shouldClose = dragX < -80
    touchStartRef.current = null
    setDragX(0)
    if (shouldClose) onClose()
  }

  return (
    <>
      {/* Backdrop overlay - only on mobile */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 md:hidden"
        onClick={onClose}
      />

      {/* Sidebar */}
      <aside
        className={`fixed md:static inset-y-0 left-0 w-[88%] max-w-sm sm:w-80 md:w-80 flex-shrink-0 bg-sidebar backdrop-blur-xl border-r border-border-primary overflow-hidden flex flex-col z-40 shadow-2xl animate-slideInLeft pt-[env(safe-area-inset-top)] md:pt-0 pb-[env(safe-area-inset-bottom)] pl-[env(safe-area-inset-left)] md:pl-0 ${
          dragX ? '' : 'transition-transform duration-200'
        }`}
        style={dragX ? { transform: `translateX(${dragX}px)` } : undefined}
        aria-label="对话历史"
        role="dialog"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        onTouchCancel={handleTouchEnd}
      >
        {/* Sidebar Header */}
        <div className="p-4 border-b border-border-primary flex items-center justify-between">
          <h2 className="text-lg font-bold text-text-primary">对话历史</h2>
          <button
            ref={closeButtonRef}
            onClick={onClose}
            className="touch-target flex items-center justify-center p-2 hover:bg-bg-tertiary rounded-full transition-colors"
            aria-label="关闭对话历史"
          >
            <X className="w-5 h-5 text-text-primary" />
          </button>
        </div>

        {/* Sidebar Content */}
        <div className="scroll-area flex-1 overflow-y-auto p-4">
          <div className="space-y-2">
            <button
              onClick={onNewChat}
              className="w-full flex items-center space-x-3 px-6 py-4 bg-gradient-main text-white rounded-2xl hover:opacity-90 transition-all shadow-xl hover:shadow-2xl hover:scale-[1.02]"
            >
              <Plus className="w-5 h-5" />
              <span className="font-semibold">新建对话</span>
            </button>

            {conversations.length === 0 && (
              <p className="px-2 py-6 text-center text-sm text-text-tertiary">还没有对话记录</p>
            )}

            {conversations.map((conv) => (
              <div
                key={conv.id}
                className={`group relative w-full rounded-2xl transition-all ${
                  conv.id === currentConversationId
                    ? 'bg-roots-50 dark:bg-road-900/20 border-2 border-roots-300 dark:border-road-400 shadow-lg'
                    : 'hover:bg-bg-tertiary border-2 border-transparent hover:shadow-md'
                }`}
              >
                {confirmingId === conv.id ? (
                  <div className="px-5 py-3 flex items-center justify-between gap-2">
                    <span className="text-sm text-text-primary truncate">删除「{conv.title}」？</span>
                    <div className="flex items-center gap-1 flex-shrink-0">
                      <button
                        onClick={() => setConfirmingId(null)}
                        className="touch-target px-3 py-1.5 text-sm rounded-full hover:bg-bg-tertiary text-text-secondary"
                      >
                        取消
                      </button>
                      <button
                        onClick={() => {
                          setConfirmingId(null)
                          onDeleteConversation(conv.id)
                        }}
                        className="touch-target px-3 py-1.5 text-sm rounded-full bg-red-600 hover:bg-red-700 text-white"
                      >
                        删除
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <button
                      onClick={() => onSelectConversation(conv.id)}
                      className="w-full text-left px-5 py-4 pr-12"
                      aria-current={conv.id === currentConversationId ? 'true' : undefined}
                    >
                      <div className="font-medium text-text-primary truncate">{conv.title}</div>
                      <div className="text-xs text-text-tertiary mt-1 truncate">
                        {modelDisplayName(conv.model_name)} • {conv.created_at ? new Date(conv.created_at).toLocaleDateString() : ''}
                      </div>
                    </button>

                    {/* Delete button: always visible on touch screens, on hover/focus on desktop */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setConfirmingId(conv.id)
                      }}
                      className="touch-target flex items-center justify-center absolute right-2 top-1/2 -translate-y-1/2 p-2 opacity-100 md:opacity-0 md:group-hover:opacity-100 focus:opacity-100 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-all"
                      title="删除对话"
                      aria-label={`删除对话 ${conv.title}`}
                    >
                      <Trash2 className="w-4 h-4 text-red-600 dark:text-red-400" />
                    </button>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      </aside>
    </>
  )
}
