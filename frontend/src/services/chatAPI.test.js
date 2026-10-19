import { afterEach, describe, expect, it, vi } from 'vitest'
import { chatAPI } from './chatAPI'

// Build a fetch Response whose body yields the given string pieces as
// separate network reads.
function streamResponse(pieces) {
  const encoder = new TextEncoder()
  const body = new ReadableStream({
    start(controller) {
      for (const piece of pieces) controller.enqueue(encoder.encode(piece))
      controller.close()
    },
  })
  return new Response(body, { status: 200 })
}

function event(obj) {
  return `data: ${JSON.stringify(obj)}\n\n`
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('chatAPI.streamChat', () => {
  it('reassembles events split across network reads', async () => {
    const full = event({ type: 'chunk', content: 'Hello' }) + event({ type: 'chunk', content: ' world' })
    // Split in the middle of the first JSON payload
    const pieces = [full.slice(0, 15), full.slice(15, 40), full.slice(40)]
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(streamResponse(pieces)))

    const chunks = []
    await chatAPI.streamChat(1, 'hi', (c) => chunks.push(c))

    expect(chunks).toEqual(['Hello', ' world'])
  })

  it('routes tool call and reasoning events to their callbacks', async () => {
    const pieces = [
      event({ type: 'reasoning', content: 'thinking' }),
      event({ type: 'tool_call', tool_id: 't1', tool_name: 'search', arguments: { q: 'x' } }),
      event({ type: 'tool_result', tool_id: 't1', success: true, result: 'ok' }),
      event({ type: 'chunk', content: 'done' }),
    ]
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(streamResponse(pieces)))

    const onChunk = vi.fn()
    const onReasoning = vi.fn()
    const onToolCall = vi.fn()
    const onToolResult = vi.fn()
    await chatAPI.streamChat(1, 'hi', onChunk, [], onReasoning, onToolCall, onToolResult)

    expect(onReasoning).toHaveBeenCalledWith('thinking')
    expect(onToolCall).toHaveBeenCalledWith({ id: 't1', name: 'search', arguments: { q: 'x' }, status: 'calling' })
    expect(onToolResult).toHaveBeenCalledWith({ tool_id: 't1', success: true, result: 'ok', error: undefined })
    expect(onChunk).toHaveBeenCalledWith('done')
  })

  it('throws when the server sends an error event', async () => {
    const pieces = [event({ type: 'chunk', content: 'partial' }), event({ type: 'error', error: 'boom' })]
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(streamResponse(pieces)))
    vi.spyOn(console, 'error').mockImplementation(() => {})

    await expect(chatAPI.streamChat(1, 'hi', () => {})).rejects.toThrow('boom')
  })

  it('throws on a non-OK HTTP status', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('nope', { status: 500 })))
    vi.spyOn(console, 'error').mockImplementation(() => {})

    await expect(chatAPI.streamChat(1, 'hi', () => {})).rejects.toThrow('500')
  })
})
