import { useEffect } from 'react'

// Keep --app-height equal to the visible viewport, so the chat input stays
// right above the on-screen keyboard. iOS Safari does not shrink 100dvh
// when the keyboard opens; it scrolls the page instead, hiding the header
// and leaving the input half-covered.
export function useAppHeight() {
  useEffect(() => {
    const viewport = window.visualViewport
    if (!viewport) return undefined

    const update = () => {
      // Ignore pinch-zoom: the visual viewport shrinks then too
      if (Math.abs(viewport.scale - 1) > 0.01) return
      document.documentElement.style.setProperty('--app-height', `${Math.round(viewport.height)}px`)
      if (window.scrollY !== 0) {
        window.scrollTo(0, 0)
      }
    }

    update()
    viewport.addEventListener('resize', update)
    viewport.addEventListener('scroll', update)
    return () => {
      viewport.removeEventListener('resize', update)
      viewport.removeEventListener('scroll', update)
      document.documentElement.style.removeProperty('--app-height')
    }
  }, [])
}
