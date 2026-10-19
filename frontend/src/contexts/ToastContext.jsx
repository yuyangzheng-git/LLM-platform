import { useCallback, useRef, useState } from 'react'
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react'
import { ToastContext } from './toastContext'

const ICONS = {
  error: AlertCircle,
  success: CheckCircle2,
  info: Info,
}

const STYLES = {
  error: 'border-red-300 dark:border-red-500/50 text-red-700 dark:text-red-300',
  success: 'border-green-300 dark:border-green-500/50 text-green-700 dark:text-green-300',
  info: 'border-border-primary text-text-primary',
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const nextId = useRef(0)

  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  // showToast('message') or showToast('message', 'success' | 'info' | 'error')
  const showToast = useCallback((message, type = 'error') => {
    const id = ++nextId.current
    setToasts((prev) => [...prev.slice(-2), { id, message, type }])
    setTimeout(() => dismiss(id), type === 'error' ? 6000 : 3000)
  }, [dismiss])

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div
        className="fixed z-50 top-4 left-1/2 -translate-x-1/2 w-[calc(100%-2rem)] max-w-md space-y-2 pointer-events-none"
        aria-live="polite"
      >
        {toasts.map((toast) => {
          const Icon = ICONS[toast.type] || Info
          return (
            <div
              key={toast.id}
              role={toast.type === 'error' ? 'alert' : 'status'}
              className={`pointer-events-auto flex items-start gap-3 px-4 py-3 rounded-xl border bg-white/95 dark:bg-bg-secondary/95 backdrop-blur-xl shadow-xl animate-fadeIn ${STYLES[toast.type] || STYLES.info}`}
            >
              <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <p className="flex-1 text-sm font-medium break-words">{toast.message}</p>
              <button
                onClick={() => dismiss(toast.id)}
                className="p-0.5 rounded hover:bg-bg-tertiary"
                aria-label="关闭提示"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )
        })}
      </div>
    </ToastContext.Provider>
  )
}
