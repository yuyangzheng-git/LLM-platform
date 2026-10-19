import { BrandTitle } from '../common/BrandTitle'

export function WelcomeScreen() {
  return (
    <div className="text-center mb-8 md:mb-12 animate-fadeIn px-4">
      <h1 className="text-[2.6rem] sm:text-6xl md:text-7xl lg:text-8xl leading-none drop-shadow-[0_2px_12px_rgba(253,252,246,0.6)] dark:drop-shadow-none">
        <BrandTitle />
      </h1>
      <p className="mt-5 md:mt-6 font-brand text-lg sm:text-xl md:text-2xl font-medium text-ink/90 dark:text-text-primary">
        今天我能帮你什么？
      </p>
      <p className="mt-2 font-display text-xs sm:text-sm tracking-[0.2em] uppercase text-text-secondary">
        由先进的 AI 大模型驱动
      </p>
    </div>
  )
}
