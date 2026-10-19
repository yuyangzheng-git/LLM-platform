import { useState } from 'react'
import { MessageSquare, Image as ImageIcon, Video } from 'lucide-react'
import { UnifiedChatInterface } from './components/unified/UnifiedChatInterface'
import { ImageGeneration } from './components/generation/ImageGeneration'
import { VideoGeneration } from './components/generation/VideoGeneration'
import { ThemeToggle } from './components/common/ThemeToggle'
import { SceneBackground, RainbowRoad } from './components/common/SceneBackground'
import { BrandTitle } from './components/common/BrandTitle'
import { useAppHeight } from './hooks/custom/useAppHeight'

const TABS = [
  { id: 'chat', name: '对话', icon: MessageSquare },
  { id: 'image', name: '图片生成', shortName: '图片', icon: ImageIcon },
  { id: 'video', name: '视频生成', shortName: '视频', icon: Video },
]

function App() {
  const [activeTab, setActiveTab] = useState('chat') // 'chat', 'image', 'video'
  useAppHeight()

  return (
    <div className="app-height relative isolate flex flex-col overflow-hidden text-text-primary pl-[env(safe-area-inset-left)] pr-[env(safe-area-inset-right)]">
      <SceneBackground />
      <RainbowRoad />

      {/* Top Navigation Bar (extends under the status bar / notch) */}
      <header className="relative z-20 flex-shrink-0 pt-[env(safe-area-inset-top)] bg-cream/70 dark:bg-bg-secondary/70 backdrop-blur-xl border-b border-border-primary/70 shadow-paper">
        <div className="max-w-7xl mx-auto px-2.5 min-[380px]:px-3 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between gap-2 h-14 md:h-16 [@media(max-height:500px)]:h-12">
            {/* Logo */}
            <div className="flex items-center min-w-0">
              <BrandTitle className="text-lg min-[400px]:text-xl sm:text-2xl md:text-[1.7rem]" />
            </div>

            <nav className="flex items-center gap-1.5 md:gap-2" aria-label="功能切换">
              {/* Desktop: labelled pills */}
              <div className="hidden md:flex items-center space-x-2">
                {TABS.map((tab) => {
                  const Icon = tab.icon
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      aria-current={activeTab === tab.id ? 'page' : undefined}
                      className={`flex items-center space-x-2 px-4 py-2 rounded-full font-display font-semibold transition-all ${
                        activeTab === tab.id
                          ? 'bg-roots-500 text-cream shadow-glow-roots'
                          : 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary/70'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span>{tab.name}</span>
                    </button>
                  )
                })}
              </div>

              {/* Phone: always-visible segmented control, label on the active tab */}
              <div className="md:hidden flex items-center p-1 rounded-full bg-cream/70 dark:bg-bg-secondary/70 border border-border-primary/70 shadow-paper">
                {TABS.map((tab) => {
                  const Icon = tab.icon
                  const active = activeTab === tab.id
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      aria-label={tab.name}
                      aria-current={active ? 'page' : undefined}
                      className={`touch-target flex items-center justify-center gap-1 h-9 rounded-full font-display font-semibold text-sm transition-all ${
                        active
                          ? 'px-2.5 min-[380px]:px-3 bg-roots-500 text-cream shadow-glow-roots'
                          : 'w-9 text-text-secondary active:bg-bg-tertiary'
                      }`}
                    >
                      <Icon className="w-[18px] h-[18px] flex-shrink-0" />
                      {active && (
                        <span className="hidden min-[380px]:inline whitespace-nowrap">{tab.shortName || tab.name}</span>
                      )}
                    </button>
                  )
                })}
              </div>

              <ThemeToggle className="touch-target bg-cream/70 dark:bg-bg-secondary/70 backdrop-blur-md shadow-paper hover:shadow-lg border border-glass" />
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area. No z-index here: it would trap the mobile
          history drawer underneath the top navigation bar. */}
      <main className="flex-1 min-h-0 overflow-hidden relative">
        {/* Tabs stay mounted so switching never loses a chat in progress
            or generated results */}
        <div className={activeTab === 'chat' ? 'h-full' : 'hidden'}>
          <UnifiedChatInterface />
        </div>
        <div className={activeTab === 'image' ? 'h-full' : 'hidden'}>
          <ImageGeneration />
        </div>
        <div className={activeTab === 'video' ? 'h-full' : 'hidden'}>
          <VideoGeneration />
        </div>
      </main>
    </div>
  )
}

export default App
