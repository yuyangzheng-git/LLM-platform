import { TOP_MODELS } from '../../config/models'

export function ChatHeader({ selectedModel }) {
  // Find current model info from TOP_MODELS
  const currentModel = TOP_MODELS.find(m => m.id === selectedModel)

  if (!currentModel) {
    return null
  }

  return (
    <div className="bg-white/70 dark:bg-bg-secondary/70 backdrop-blur-xl px-3 sm:px-4 md:px-6 py-2 md:py-3 rounded-xl md:rounded-2xl shadow-lg border border-glass">
      <div className="text-xs sm:text-sm font-medium bg-gradient-to-r from-orange-600 via-amber-600 to-rose-600 dark:from-amber-400 dark:via-orange-400 dark:to-rose-400 bg-clip-text text-transparent whitespace-nowrap">
        {currentModel.provider} • {currentModel.name}
      </div>
    </div>
  )
}
