import { useState } from 'react'
import { MessageSquare, Image as ImageIcon, Video, Menu } from 'lucide-react'
import { UnifiedChatInterface } from './unified/UnifiedChatInterface'
import { ImageGeneration } from './generation/ImageGeneration'
import { VideoGeneration } from './generation/VideoGeneration'
import { ThemeToggle } from './common/ThemeToggle'

export function App() {
  const [activeTab, setActiveTab] = useState('chat') // 'chat', 'image', 'video'
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const tabs = [
    { id: 'chat', name: '对话', icon: MessageSquare },
    { id: 'image', name: '图片生成', icon: ImageIcon },
    { id: 'video', name: '视频生成', icon: Video },
  ]

  return (
    <div className="h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-rose-50 dark:from-stone-900 dark:via-amber-950 dark:to-orange-950 flex flex-col overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -right-1/2 w-full h-full bg-gradient-to-br from-orange-400/10 to-rose-400/10 dark:from-amber-600/5 dark:to-orange-600/5 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute -bottom-1/2 -left-1/2 w-full h-full bg-gradient-to-tr from-amber-400/10 to-pink-400/10 dark:from-yellow-600/5 dark:to-rose-600/5 rounded-full blur-3xl animate-pulse-slow delay-1000"></div>
      </div>

      {/* Top Navigation Bar */}
      <div className="relative z-20 flex-shrink-0 bg-white/70 dark:bg-bg-secondary/70 backdrop-blur-xl border-b border-border-primary shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="text-2xl font-black bg-gradient-to-r from-orange-500 via-amber-500 to-rose-500 dark:from-amber-400 dark:via-orange-400 dark:to-rose-400 bg-clip-text text-transparent">
                Zachary's LLM
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-2">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-xl font-medium transition-all ${
                      activeTab === tab.id
                        ? 'bg-gradient-main text-white shadow-lg'
                        : 'text-text-primary hover:bg-bg-tertiary'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{tab.name}</span>
                  </button>
                )
              })}
              <ThemeToggle className="ml-2 bg-white/70 dark:bg-bg-secondary/70 backdrop-blur-md shadow-lg hover:shadow-xl border border-glass" />
            </div>

            {/* Mobile Menu Button */}
            <div className="md:hidden flex items-center space-x-2">
              <ThemeToggle className="bg-white/70 dark:bg-bg-secondary/70 backdrop-blur-md shadow-lg hover:shadow-xl border border-glass" />
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="p-2 rounded-lg bg-white/70 dark:bg-bg-secondary/70 backdrop-blur-md shadow-lg hover:shadow-xl border border-glass"
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
                    className={`w-full flex items-center space-x-2 px-4 py-3 rounded-xl font-medium transition-all ${
                      activeTab === tab.id
                        ? 'bg-gradient-main text-white shadow-lg'
                        : 'bg-white/50 dark:bg-bg-secondary/50 text-text-primary hover:bg-bg-tertiary'
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

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden relative z-10">
        {activeTab === 'chat' && <UnifiedChatInterface />}
        {activeTab === 'image' && <ImageGeneration />}
        {activeTab === 'video' && <VideoGeneration />}
      </div>
    </div>
  )
}
