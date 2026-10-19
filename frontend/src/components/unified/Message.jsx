import { memo, useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Paperclip, ChevronDown, ChevronUp, Brain, AlertCircle } from 'lucide-react'
import { useTheme } from '../../hooks/custom/useTheme'
import ToolCallDisplay from './ToolCallDisplay'
import { TypingIndicator } from './TypingIndicator'
import { CopyButton } from '../common/CopyButton'

// Markdown components with theme support
const createMarkdownComponents = (theme) => ({
  // react-markdown v9 no longer passes `inline`: a fenced block is one with
  // a language class or a newline in it, everything else is inline code.
  code({ node, className, children, ...props }) {
    const match = /language-(\w+)/.exec(className || '')
    const text = String(children)
    const isBlock = Boolean(match) || text.includes('\n')
    return isBlock ? (
      <div className="relative group my-4">
        <div className="absolute right-2 top-2 z-10 opacity-100 md:opacity-0 md:group-hover:opacity-100 focus-within:opacity-100 transition-opacity">
          <CopyButton
            text={text.replace(/\n$/, '')}
            label="复制代码"
            showLabel
            className="px-3 py-1 bg-bg-tertiary hover:bg-bg-secondary text-text-primary text-xs rounded shadow-md"
          />
        </div>
        <SyntaxHighlighter
          style={theme === 'dark' ? oneDark : oneLight}
          language={match ? match[1] : 'text'}
          PreTag="div"
          customStyle={{
            margin: 0,
            borderRadius: '0.75rem',
            fontSize: '0.875rem',
            maxWidth: '100%',
            overflowX: 'auto',
          }}
          {...props}
        >
          {text.replace(/\n$/, '')}
        </SyntaxHighlighter>
      </div>
    ) : (
      <code
        className="bg-bg-tertiary text-text-primary px-1.5 py-0.5 rounded text-sm font-mono break-words"
        {...props}
      >
        {children}
      </code>
    )
  },
  // The code renderer above draws its own block, so skip the extra <pre>
  pre({ children }) {
    return <>{children}</>
  },
  p({ children }) {
    return <p className="mb-4 last:mb-0 leading-relaxed text-base break-words">{children}</p>
  },
  ul({ children }) {
    return <ul className="list-disc list-inside mb-4 space-y-2 pl-4">{children}</ul>
  },
  ol({ children }) {
    return <ol className="list-decimal list-inside mb-4 space-y-2 pl-4">{children}</ol>
  },
  li({ children }) {
    return <li className="leading-relaxed">{children}</li>
  },
  blockquote({ children }) {
    return (
      <blockquote className="border-l-4 border-orange-500 dark:border-amber-400 pl-4 py-2 my-4 bg-orange-50 dark:bg-amber-900/20 rounded-r-lg break-words overflow-wrap-anywhere">
        {children}
      </blockquote>
    )
  },
  table({ children }) {
    return (
      <div className="overflow-x-auto my-4">
        <table className="min-w-full border-collapse border border-border-primary rounded-lg overflow-hidden">
          {children}
        </table>
      </div>
    )
  },
  thead({ children }) {
    return (
      <thead className="bg-orange-100 dark:bg-amber-900/30">
        {children}
      </thead>
    )
  },
  tbody({ children }) {
    return <tbody className="divide-y divide-border-primary">{children}</tbody>
  },
  tr({ children }) {
    return <tr className="hover:bg-bg-tertiary/50 transition-colors">{children}</tr>
  },
  th({ children }) {
    return (
      <th className="px-4 py-2 text-left font-semibold border-r border-border-primary last:border-r-0">
        {children}
      </th>
    )
  },
  td({ children }) {
    return (
      <td className="px-4 py-2 border-r border-border-primary last:border-r-0">
        {children}
      </td>
    )
  },
  h1({ children }) {
    return <h1 className="text-3xl font-bold mb-4 mt-6 first:mt-0 text-gradient-primary">{children}</h1>
  },
  h2({ children }) {
    return <h2 className="text-2xl font-bold mb-3 mt-5 first:mt-0 text-gradient-primary">{children}</h2>
  },
  h3({ children }) {
    return <h3 className="text-xl font-bold mb-3 mt-4 first:mt-0">{children}</h3>
  },
  h4({ children }) {
    return <h4 className="text-lg font-bold mb-2 mt-3 first:mt-0">{children}</h4>
  },
  a({ children, href }) {
    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-orange-600 dark:text-amber-400 hover:underline"
      >
        {children}
      </a>
    )
  },
  hr() {
    return <hr className="my-6 border-t-2 border-border-primary" />
  },
  strong({ children }) {
    return <strong className="font-bold text-text-primary">{children}</strong>
  },
  em({ children }) {
    return <em className="italic text-text-secondary">{children}</em>
  },
})

export const Message = memo(function Message({ message }) {
  const { theme } = useTheme()
  const [showReasoning, setShowReasoning] = useState(false)

  // Memoize markdown components to avoid recreation on every render
  const markdownComponents = useMemo(() => createMarkdownComponents(theme), [theme])

  const isAssistant = message.role === 'assistant'
  const hasToolCalls = isAssistant && message.tool_calls?.length > 0
  const isThinking =
    isAssistant && message.isStreaming && !message.content && !message.reasoning && !hasToolCalls

  return (
    <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}>
      <div
        className={`max-w-full md:max-w-3xl min-w-0 break-words ${
          message.role === 'user'
            ? 'bg-gradient-message-user text-white rounded-2xl md:rounded-[2rem] px-4 sm:px-6 md:px-8 py-3 sm:py-4 md:py-5 shadow-xl hover:shadow-2xl transition-all'
            : 'bg-message-assistant backdrop-blur-xl border border-border-primary rounded-2xl md:rounded-[2rem] px-4 sm:px-6 md:px-8 py-4 sm:py-5 md:py-6 shadow-lg hover:shadow-xl transition-all'
        }`}
      >
        {/* File indicator for user messages */}
        {message.role === 'user' && message.fileCount > 0 && (
          <div className="flex items-center space-x-2 mb-3 pb-3 border-b border-white/20">
            <Paperclip className="w-4 h-4" />
            <span className="text-sm opacity-90">
              已附加 {message.fileCount} 个文件
            </span>
          </div>
        )}

        {isThinking && <TypingIndicator />}

        {/* Reasoning/Thinking process for assistant messages */}
        {isAssistant && message.reasoning && (
          <div className="mb-4 pb-4 border-b border-border-primary">
            <button
              onClick={() => setShowReasoning(!showReasoning)}
              className="flex items-center space-x-2 text-text-secondary hover:text-text-primary transition-colors w-full group"
              aria-expanded={showReasoning}
            >
              <Brain className="w-4 h-4 text-orange-500 dark:text-amber-400" />
              <span className="text-sm font-medium">
                {message.isStreaming && !message.content ? '正在思考…' : '思考过程'}
              </span>
              {showReasoning ? (
                <ChevronUp className="w-4 h-4 ml-auto group-hover:translate-y-[-2px] transition-transform" />
              ) : (
                <ChevronDown className="w-4 h-4 ml-auto group-hover:translate-y-[2px] transition-transform" />
              )}
            </button>
            {showReasoning && (
              <div className="mt-3 p-4 bg-orange-50/50 dark:bg-amber-900/10 rounded-xl border border-orange-200/50 dark:border-amber-400/20 animate-fadeIn">
                <div className="text-sm text-text-secondary italic leading-relaxed whitespace-pre-wrap">
                  {message.reasoning}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tool calls, live while streaming and restored from history */}
        {hasToolCalls && <ToolCallDisplay toolCalls={message.tool_calls} />}

        {message.content && (
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
            {message.content}
          </ReactMarkdown>
        )}

        {message.stopped && (
          <p className="mt-3 text-sm text-text-tertiary italic">已停止生成</p>
        )}

        {message.isError && (
          <div
            role="alert"
            className="mt-3 flex items-start gap-2 text-sm text-red-700 dark:text-red-300 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-500/30 rounded-xl px-3 py-2"
          >
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>{message.error || '抱歉，发生了错误。请稍后重试。'}</span>
          </div>
        )}

        {/* Copy button for finished assistant messages */}
        {isAssistant && !message.isStreaming && message.content && (
          <div className="flex items-center space-x-2 mt-4 pt-3 border-t border-border-primary">
            <CopyButton
              text={message.content}
              label="复制内容"
              className="p-1.5 hover:bg-bg-tertiary rounded transition-colors text-text-secondary"
            />
          </div>
        )}
      </div>
    </div>
  )
})
