export function TypingIndicator() {
  return (
    <div className="flex items-center space-x-2 px-4 sm:px-5 md:px-6 py-3 md:py-4 rounded-xl md:rounded-2xl bg-white/60 dark:bg-bg-secondary/60 backdrop-blur-lg border border-border-primary shadow-lg max-w-fit">
      <div className="flex space-x-1.5">
        <div className="w-2 h-2 bg-gradient-to-r from-orange-500 to-amber-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        <div className="w-2 h-2 bg-gradient-to-r from-amber-500 to-rose-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="w-2 h-2 bg-gradient-to-r from-rose-500 to-pink-500 rounded-full animate-bounce"></div>
      </div>
      <span className="text-xs sm:text-sm text-text-secondary dark:text-text-secondary ml-2">AI正在思考...</span>
    </div>
  )
}
