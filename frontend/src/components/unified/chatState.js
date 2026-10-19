// Pure helpers for chat state, kept separate so they can be unit tested.

// Sent when the user attaches files without typing anything; the backend
// requires a non-empty message.
export const FILES_ONLY_PROMPT = '请查看附件内容'

let keySeq = 0

// Stable React key for a message or attachment. Messages from the server
// use their database id; locally created ones get a unique local key, so
// the two can never collide.
export function newKey(prefix = 'local') {
  keySeq += 1
  return `${prefix}-${keySeq}`
}

export function withKey(message) {
  return { ...message, key: message.id ? `db-${message.id}` : newKey() }
}

export function addToolCall(toolCalls = [], toolCall) {
  return [...toolCalls, { ...toolCall, status: 'calling' }]
}

export function applyToolResult(toolCalls = [], toolResult) {
  return toolCalls.map((call) =>
    call.id === toolResult.tool_id
      ? {
          ...call,
          status: toolResult.success ? 'completed' : 'error',
          result: toolResult.result,
          error: toolResult.error,
        }
      : call
  )
}

// ?c=<id> in the address bar keeps the open conversation across reloads
export function readConversationIdFromUrl(search = window.location.search) {
  const value = Number(new URLSearchParams(search).get('c'))
  return Number.isInteger(value) && value > 0 ? value : null
}

export function writeConversationIdToUrl(id) {
  const url = new URL(window.location.href)
  if (id) {
    url.searchParams.set('c', String(id))
  } else {
    url.searchParams.delete('c')
  }
  window.history.replaceState(null, '', url)
}

export function uploadErrorMessage(err) {
  return err?.response?.data?.detail || err?.message || '上传失败'
}

// True while an IME (e.g. Chinese pinyin) is composing. Safari fires
// compositionend before keydown, so the composition flag alone is not enough.
export function isImeEnter(e, isComposing) {
  return Boolean(isComposing || e.nativeEvent?.isComposing || e.keyCode === 229)
}
