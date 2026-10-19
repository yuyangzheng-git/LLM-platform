import { useEffect, useRef, useState } from 'react'
import { Check, Copy } from 'lucide-react'

// Copy-to-clipboard button that confirms with a check mark for a moment
export function CopyButton({ text, label = '复制', showLabel = false, className = '' }) {
  const [copied, setCopied] = useState(false)
  const timerRef = useRef(null)

  useEffect(() => () => clearTimeout(timerRef.current), [])

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      clearTimeout(timerRef.current)
      timerRef.current = setTimeout(() => setCopied(false), 1500)
    } catch {
      setCopied(false)
    }
  }

  const Icon = copied ? Check : Copy
  const currentLabel = copied ? '已复制' : label

  return (
    <button
      onClick={handleCopy}
      className={`flex items-center space-x-1 ${className}`}
      title={currentLabel}
      aria-label={currentLabel}
    >
      <Icon className={`w-4 h-4 ${copied ? 'text-green-600 dark:text-green-400' : ''}`} />
      {showLabel && <span>{currentLabel}</span>}
    </button>
  )
}
