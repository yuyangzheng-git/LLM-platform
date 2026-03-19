import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  MessageSquarePlus,
  Globe,
  FileText,
  Presentation,
  Table2,
  Search,
  Code,
  Sparkles,
  Clock,
  Smartphone,
  User,
  PanelLeft,
  ChevronDown
} from 'lucide-react'
import { useState } from 'react'

function Layout({ children }) {
  const location = useLocation()
  const navigate = useNavigate()
  const [isCollapsed, setIsCollapsed] = useState(false)

  const mainMenuItems = [
    { id: 'websites', icon: Globe, label: 'Websites', path: '/websites' },
    { id: 'docs', icon: FileText, label: 'Docs', path: '/docs' },
    { id: 'slides', icon: Presentation, label: 'Slides', path: '/slides' },
    { id: 'sheets', icon: Table2, label: 'Sheets', path: '/sheets' },
    { id: 'research', icon: Search, label: 'Deep Research', path: '/research' },
    { id: 'code', icon: Code, label: 'Kimi Code', path: '/code' },
    { id: 'claw', icon: Sparkles, label: 'Kimi Claw', path: '/claw', beta: true },
  ]

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className={`${isCollapsed ? 'w-16' : 'w-64'} bg-white border-r border-gray-200 transition-all duration-300 flex flex-col`}>
        {/* Header */}
        <div className="p-4 flex items-center justify-between border-b border-gray-200">
          {!isCollapsed && (
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center text-white font-bold text-lg">
                K
              </div>
            </Link>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <PanelLeft className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* New Chat Button */}
        <div className="p-4">
          <button
            onClick={() => navigate('/settings')}
            className="w-full flex items-center justify-between px-4 py-3 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors group"
          >
            <div className="flex items-center space-x-3">
              <MessageSquarePlus className="w-5 h-5 text-gray-700" />
              {!isCollapsed && <span className="font-medium text-gray-700">New Chat</span>}
            </div>
            {!isCollapsed && (
              <div className="flex items-center space-x-1 text-xs text-gray-500">
                <kbd className="px-1.5 py-0.5 bg-white rounded border border-gray-300">⌘</kbd>
                <kbd className="px-1.5 py-0.5 bg-white rounded border border-gray-300">K</kbd>
              </div>
            )}
          </button>
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 px-2 space-y-1 overflow-y-auto">
          {mainMenuItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path

            return (
              <Link
                key={item.id}
                to={item.path}
                className={`flex items-center justify-between px-3 py-2.5 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-gray-100 text-gray-900'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className="w-5 h-5" />
                  {!isCollapsed && <span className="text-sm font-medium">{item.label}</span>}
                </div>
                {!isCollapsed && item.beta && (
                  <span className="text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full">
                    Beta
                  </span>
                )}
              </Link>
            )
          })}

          {/* Chat History Section */}
          <div className="pt-4 mt-4 border-t border-gray-200">
            <Link
              to="/history"
              className={`flex items-center justify-between px-3 py-2.5 rounded-lg transition-colors ${
                location.pathname === '/history'
                  ? 'bg-gray-100 text-gray-900'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Clock className="w-5 h-5" />
                {!isCollapsed && <span className="text-sm font-medium">Chat History</span>}
              </div>
            </Link>
            {!isCollapsed && (
              <p className="px-3 py-2 text-xs text-gray-500">
                Log in to sync chat history
              </p>
            )}
          </div>
        </nav>

        {/* Bottom Section */}
        <div className="border-t border-gray-200 p-2 space-y-1">
          <button className="w-full flex items-center space-x-3 px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
            <Smartphone className="w-5 h-5" />
            {!isCollapsed && <span className="text-sm font-medium">Mobile App</span>}
          </button>

          <button className="w-full flex items-center justify-between px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
            <div className="flex items-center space-x-3">
              <User className="w-5 h-5" />
              {!isCollapsed && <span className="text-sm font-medium">Log In</span>}
            </div>
            {!isCollapsed && <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-hidden bg-white">
        {children}
      </main>
    </div>
  )
}

export default Layout
