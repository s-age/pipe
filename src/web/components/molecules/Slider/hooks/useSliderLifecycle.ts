import { useEffect, useRef, useState } from 'react'

export type UseSliderLifecycleReturn = {
  measuredWidth: number
  containerRef: (element: HTMLDivElement | null) => void
}

/**
 * useSliderLifecycle
 *
 * Manages Slider lifecycle effects (ResizeObserver).
 * Pattern: Lifecycle (separated from Handlers per hooks.md)
 */
export const useSliderLifecycle = (): UseSliderLifecycleReturn => {
  const [measuredWidth, setMeasuredWidth] = useState<number>(300)
  const containerReference = useRef<HTMLDivElement | null>(null)

  useEffect((): (() => void) | undefined => {
    if (typeof window === 'undefined' || !('ResizeObserver' in window)) return undefined

    let rafId: number | null = null
    const ro = new ResizeObserver((entries) => {
      const entry = entries[0]
      if (!entry) return
      const width = Math.max(0, Math.floor(entry.contentRect.width))
      // throttle to rAF
      if (rafId !== null) cancelAnimationFrame(rafId)
      rafId = requestAnimationFrame(() => {
        setMeasuredWidth(width || 300)
        rafId = null
      })
    })

    if (containerReference.current) ro.observe(containerReference.current)

    return (): void => {
      ro.disconnect()
      if (rafId !== null) cancelAnimationFrame(rafId)
    }
  }, [])

  return {
    measuredWidth,
    containerRef: (element: HTMLDivElement | null): void => {
      containerReference.current = element
    }
  }
}
