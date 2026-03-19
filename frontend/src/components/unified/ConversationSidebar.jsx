import { Plus, X, Trash2 } from 'lucide-react'

export function ConversationSidebar({
  isOpen,
  onClose,
  conversations = [],
  currentConversationId,
  onSelectConversation,
  onDeleteConversation,
  onNewChat,
}) {
  if (!isOpen) return null

  return (
    <>
      {/* Backdrop overlay - only on mobile */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 md:hidden"
        onClick={onClose}
      />

      {/* Sidebar */}
      <div className="fixed md:static inset-y-0 left-0 w-full sm:w-80 md:w-80 transition-all duration-300 bg-sidebar backdrop-blur-xl border-r border-border-primary overflow-hidden flex flex-col z-40 shadow-2xl animate-slideInLeft">
        {/* Sidebar Header */}
        <div className="p-4 border-b border-border-primary flex items-center justify-between">
          <h2 className="text-lg font-bold text-text-primary">对话历史</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-bg-tertiary rounded-lg transition-colors"
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

            {conversations.map((conv) => (
              <div
                key={conv.id}
                className={`group relative w-full rounded-2xl transition-all ${
                  conv.id === currentConversationId
                    ? 'bg-orange-50 dark:bg-amber-900/20 border-2 border-orange-300 dark:border-amber-400 shadow-lg'
                    : 'hover:bg-bg-tertiary border-2 border-transparent hover:shadow-md'
                }`}
              >
                <button
                  onClick={() => onSelectConversation(conv.id)}
                  className="w-full text-left px-5 py-4 pr-12"
                >
                  <div className="font-medium text-text-primary truncate">{conv.title}</div>
                  <div className="text-xs text-text-tertiary mt-1">
                    {conv.model_provider} • {new Date(conv.created_at).toLocaleDateString()}
                  </div>
                </button>

                {/* Delete button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    onDeleteConversation(conv.id)
                  }}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-2 opacity-0 group-hover:opacity-100 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-all"
                  title="删除对话"
                >
                  <Trash2 className="w-4 h-4 text-red-600 dark:text-red-400" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  )
}
