import { X } from 'lucide-react'

export function SettingsPanel({
  isOpen,
  onClose,
  providers = [],
  selectedProvider,
  onProviderChange,
  availableModels = [],
  selectedModel,
  onModelChange,
}) {
  if (!isOpen) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/30 dark:bg-black/50 backdrop-blur-sm z-40 animate-fadeIn"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="fixed top-0 right-0 h-full w-96 bg-bg-secondary backdrop-blur-xl border-l border-border-primary shadow-2xl z-50 animate-slideInRight overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-border-primary flex items-center justify-between sticky top-0 bg-bg-secondary z-10">
          <h2 className="text-xl font-bold text-text-primary">Model Settings</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-bg-tertiary rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-text-primary" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Model Provider - Read-only display */}
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              AI Provider
            </label>
            <div className="w-full px-5 py-3 border-2 border-border-primary rounded-2xl bg-bg-tertiary text-text-primary font-medium">
              {selectedProvider ? selectedProvider.toUpperCase() : 'OpenAI'}
            </div>
            <p className="text-xs text-text-tertiary mt-2">
              Pre-configured by system administrator
            </p>
          </div>

          {/* Model Selection */}
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              Model
            </label>
            <select
              value={selectedModel}
              onChange={(e) => onModelChange(e.target.value)}
              className="w-full px-5 py-3 border-2 border-border-primary rounded-2xl focus:ring-2 focus:ring-orange-500 dark:focus:ring-amber-500 focus:border-orange-500 dark:focus:border-amber-500 bg-bg-primary text-text-primary hover:border-border-secondary transition-all shadow-sm font-medium"
            >
              {availableModels.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
            <p className="text-xs text-text-tertiary mt-2">
              {availableModels.length} models available
            </p>
          </div>

          {/* Model Info */}
          <div className="bg-orange-50 dark:bg-amber-900/20 border border-orange-200 dark:border-amber-400/30 rounded-2xl p-4">
            <h3 className="text-sm font-semibold text-orange-900 dark:text-amber-200 mb-2">
              ℹ️ Model Information
            </h3>
            <ul className="text-xs text-orange-700 dark:text-amber-300 space-y-1">
              <li>• Different models have different capabilities</li>
              <li>• Newer models (like GPT-4o) are more powerful</li>
              <li>• Mini models are faster and more economical</li>
            </ul>
          </div>
        </div>
      </div>
    </>
  )
}
