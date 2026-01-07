import { useEffect, useRef } from 'react'

import type { ToastItem as ToastItemType } from '@/stores/useAppStore'

type UseToastItemLifecycleProperties = {
  exiting: boolean
  hovering: boolean
  item: ToastItemType
  onExit: () => void
}

export const useToastItemLifecycle = ({
  exiting,
  hovering,
  item,
  onExit
}: UseToastItemLifecycleProperties): void => {
  const autoTimerReference = useRef<number | null>(null)
  const startAtReference = useRef<number | null>(null)
  const remainingReference = useRef<number | null>(item.duration ?? null)

  // Timer management effect
  useEffect(() => {
    remainingReference.current = item.duration ?? null

    const startTimer = (ms: number): void => {
      startAtReference.current = Date.now()
      autoTimerReference.current = window.setTimeout(() => {
        onExit()
      }, ms)
    }

    if (remainingReference.current != null) startTimer(remainingReference.current)

    return (): void => {
      if (autoTimerReference.current) {
        clearTimeout(autoTimerReference.current)
        autoTimerReference.current = null
      }
    }
  }, [item.duration, item.id, onExit])

  // Hover effect
  useEffect(() => {
    if (hovering) {
      if (autoTimerReference.current && startAtReference.current) {
        const elapsed = Date.now() - startAtReference.current
        remainingReference.current = Math.max(
          0,
          (remainingReference.current ?? 0) - elapsed
        )
        clearTimeout(autoTimerReference.current)
        autoTimerReference.current = null
      }
    } else {
      if (
        !autoTimerReference.current &&
        remainingReference.current != null &&
        !exiting
      ) {
        startAtReference.current = Date.now()
        autoTimerReference.current = window.setTimeout(() => {
          onExit()
        }, remainingReference.current)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hovering, exiting])
}
