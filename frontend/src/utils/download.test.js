import { afterEach, describe, expect, it, vi } from 'vitest'
import { downloadFile } from './download'

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

describe('downloadFile', () => {
  it('opens a new tab instead of navigating away when the fetch is blocked', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    const open = vi.fn()
    vi.stubGlobal('window', { open })

    const result = await downloadFile('https://cdn.example.com/a.png', 'a.png')

    expect(result).toBe('opened')
    expect(open).toHaveBeenCalledWith('https://cdn.example.com/a.png', '_blank', 'noopener,noreferrer')
  })

  it('opens a new tab when the server returns an error status', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('', { status: 403 })))
    const open = vi.fn()
    vi.stubGlobal('window', { open })

    expect(await downloadFile('https://cdn.example.com/a.png', 'a.png')).toBe('opened')
  })
})
