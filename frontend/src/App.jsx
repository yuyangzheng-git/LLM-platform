import { useState } from 'react'
import { MessageSquare, Image as ImageIcon, Video, Menu } from 'lucide-react'
import { UnifiedChatInterface } from './components/unified/UnifiedChatInterface'
import { ImageGeneration } from './components/generation/ImageGeneration'
import { VideoGeneration } from './components/generation/VideoGeneration'
import { ThemeToggle } from './components/common/ThemeToggle'
import { SceneBackground, RainbowRoad } from './components/common/SceneBackground'
import { BrandTitle } from './components/common/BrandTitle'

function App() {
  const [activeTab, setActiveTab] = useState('chat') // 'chat', 'image', 'video'
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const tabs = [
    { id: 'chat', name: '对话', icon: MessageSquare },
    { id: 'image', name: '图片生成', icon: ImageIcon },
    { id: 'video', name: '视频生成', icon: Video },
  ]

  return (
    <div className="relative isolate h-screen h-[100dvh] flex flex-col overflow-hidden text-text-primary">
      <SceneBackground />
      <RainbowRoad />

      {/* Top Navigation Bar */}
      <div className="relative z-20 flex-shrink-0 bg-cream/70 dark:bg-bg-secondary/70 backdrop-blur-xl border-b border-border-primary/70 shadow-paper">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center">
              <BrandTitle className="text-2xl sm:text-[1.7rem]" />
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-2">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
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
              <ThemeToggle className="ml-2 bg-cream/70 dark:bg-bg-secondary/70 backdrop-blur-md shadow-paper hover:shadow-lg border border-glass" />
            </div>

            {/* Mobile Menu Button */}
            <div className="md:hidden flex items-center space-x-2">
              <ThemeToggle className="bg-cream/70 dark:bg-bg-secondary/70 backdrop-blur-md shadow-lg hover:shadow-xl border border-glass" />
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                aria-label="切换功能菜单"
                aria-expanded={isMobileMenuOpen}
                className="p-2 rounded-lg bg-cream/70 dark:bg-bg-secondary/70 backdrop-blur-md shadow-lg hover:shadow-xl border border-glass"
              >
                <Menu className="w-6 h-6 text-text-primary" />
              </button>
            </div>
          </div>

          {/* Mobile Menu */}
          {isMobileMenuOpen && (
            <div className="md:hidden pb-4 space-y-2 animate-fadeIn">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => {
                      setActiveTab(tab.id)
                      setIsMobileMenuOpen(false)
                    }}
                    className={`w-full flex items-center space-x-2 px-4 py-3 rounded-full font-display font-semibold transition-all ${
                      activeTab === tab.id
                        ? 'bg-roots-500 text-cream shadow-glow-roots'
                        : 'bg-cream/60 dark:bg-bg-secondary/50 text-text-primary hover:bg-bg-tertiary'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{tab.name}</span>
                  </button>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {/* Main Content Area. No z-index here: it would trap the mobile
          history drawer underneath the top navigation bar. */}
      <div className="flex-1 overflow-hidden relative">
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
      </div>
    </div>
  )
}

export default App
