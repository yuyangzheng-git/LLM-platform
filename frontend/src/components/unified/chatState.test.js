import { describe, expect, it } from 'vitest'
import {
  addToolCall,
  applyToolResult,
  isImeEnter,
  newKey,
  readConversationIdFromUrl,
  withKey,
} from './chatState'

describe('message keys', () => {
  it('never collide between server and local messages', () => {
    // A server message with id 40 and a local message created when the list
    // already holds 40 items used to share the key "40"
    const fromServer = withKey({ id: 40, role: 'user', content: 'a' })
    const local = withKey({ role: 'user', content: 'b' })
    expect(fromServer.key).toBe('db-40')
    expect(local.key).not.toBe(fromServer.key)
    expect(newKey()).not.toBe(newKey())
  })
})

describe('tool call updates', () => {
  it('adds a call and then completes it by id', () => {
    let calls = addToolCall([], { id: 't1', name: 'web_search', arguments: { q: 'x' } })
    calls = addToolCall(calls, { id: 't2', name: 'get_current_datetime', arguments: {} })
    expect(calls.map((c) => c.status)).toEqual(['calling', 'calling'])

    calls = applyToolResult(calls, { tool_id: 't2', success: false, error: 'boom' })
    expect(calls[0].status).toBe('calling')
    expect(calls[1]).toMatchObject({ status: 'error', error: 'boom' })
  })
})

describe('isImeEnter', () => {
  it('detects composition from state, the native event, or keyCode 229', () => {
    expect(isImeEnter({ nativeEvent: {} }, true)).toBe(true)
    expect(isImeEnter({ nativeEvent: { isComposing: true } }, false)).toBe(true)
    expect(isImeEnter({ nativeEvent: {}, keyCode: 229 }, false)).toBe(true)
    expect(isImeEnter({ nativeEvent: {}, keyCode: 13 }, false)).toBe(false)
  })
})

describe('readConversationIdFromUrl', () => {
  it('accepts positive integer ids only', () => {
    expect(readConversationIdFromUrl('?c=12')).toBe(12)
    expect(readConversationIdFromUrl('?c=abc')).toBeNull()
    expect(readConversationIdFromUrl('?c=-1')).toBeNull()
    expect(readConversationIdFromUrl('')).toBeNull()
  })
})
