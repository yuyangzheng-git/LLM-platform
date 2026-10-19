import { useState } from 'react'
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

  if (!isOpen) return null

  return (
    <>
      {/* Backdrop overlay - only on mobile */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 md:hidden"
        onClick={onClose}
      />

      {/* Sidebar */}
      <aside
        className="fixed md:static inset-y-0 left-0 w-full sm:w-80 md:w-80 flex-shrink-0 transition-all duration-300 bg-sidebar backdrop-blur-xl border-r border-border-primary overflow-hidden flex flex-col z-40 shadow-2xl animate-slideInLeft"
        aria-label="对话历史"
      >
        {/* Sidebar Header */}
        <div className="p-4 border-b border-border-primary flex items-center justify-between">
          <h2 className="text-lg font-bold text-text-primary">对话历史</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-bg-tertiary rounded-lg transition-colors"
            aria-label="关闭对话历史"
          >
            <X className="w-5 h-5 text-text-primary" />
          </button>
        </div>

        {/* Sidebar Content */}
        <div className="flex-1 overflow-y-auto p-4">
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
                    ? 'bg-orange-50 dark:bg-amber-900/20 border-2 border-orange-300 dark:border-amber-400 shadow-lg'
                    : 'hover:bg-bg-tertiary border-2 border-transparent hover:shadow-md'
                }`}
              >
                {confirmingId === conv.id ? (
                  <div className="px-5 py-3 flex items-center justify-between gap-2">
                    <span className="text-sm text-text-primary truncate">删除「{conv.title}」？</span>
                    <div className="flex items-center gap-1 flex-shrink-0">
                      <button
                        onClick={() => setConfirmingId(null)}
                        className="px-2.5 py-1 text-sm rounded-lg hover:bg-bg-tertiary text-text-secondary"
                      >
                        取消
                      </button>
                      <button
                        onClick={() => {
                          setConfirmingId(null)
                          onDeleteConversation(conv.id)
                        }}
                        className="px-2.5 py-1 text-sm rounded-lg bg-red-600 hover:bg-red-700 text-white"
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
                      className="absolute right-3 top-1/2 -translate-y-1/2 p-2 opacity-100 md:opacity-0 md:group-hover:opacity-100 focus:opacity-100 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-all"
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
