export function WelcomeScreen() {
  return (
    <div className="text-center mb-8 md:mb-12 animate-fadeIn px-4">
      <div className="relative inline-block mb-4 md:mb-6">
        <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-8xl font-black bg-gradient-to-r from-orange-500 via-amber-500 to-rose-500 dark:from-amber-400 dark:via-orange-400 dark:to-rose-400 bg-clip-text text-transparent animate-pulse-slow">
          Zachary's LLM
        </h1>
        <div className="absolute -inset-4 bg-gradient-to-r from-orange-400/20 via-amber-400/20 to-rose-400/20 blur-2xl -z-10"></div>
      </div>
      <p className="text-text-secondary text-base sm:text-lg md:text-xl font-medium">今天我能帮你什么？</p>
      <p className="text-text-tertiary text-xs sm:text-sm mt-2">由先进的AI大模型驱动</p>
    </div>
  )
}
