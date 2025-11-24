import { useCallback, useEffect, useRef, useState } from 'react'

import type { ToastItem as ToastItemType } from '@/stores/useAppStore'

const ANIM_DURATION = 180

export const useToastItemLifecycle = (
  item: ToastItemType,
  removeToast: (id: string) => void
): {
  hovering: boolean
  exiting: boolean
  handleMouseEnter: () => void
  handleMouseLeave: () => void
  handleClose: () => void
  statusClass: 'statusSuccess' | 'statusFailure' | 'statusWarning'
} => {
  const autoTimerReference = useRef<number | null>(null)
  const finishTimerReference = useRef<number | null>(null)
  const startAtReference = useRef<number | null>(null)
  const remainingReference = useRef<number | null>(item.duration ?? null)
  const [hovering, setHovering] = useState(false)
  const [exiting, setExiting] = useState(false)

  useEffect(() => {
    remainingReference.current = item.duration ?? null

    const startTimer = (ms: number): void => {
      startAtReference.current = Date.now()
      autoTimerReference.current = window.setTimeout(() => {
        setExiting(true)
        finishTimerReference.current = window.setTimeout(
          () => removeToast(item.id),
          ANIM_DURATION
        )
      }, ms)
    }

    if (remainingReference.current != null) startTimer(remainingReference.current)

    return (): void => {
      if (autoTimerReference.current) {
        clearTimeout(autoTimerReference.current)
        autoTimerReference.current = null
      }
      if (finishTimerReference.current) {
        clearTimeout(finishTimerReference.current)
        finishTimerReference.current = null
      }
    }
  }, [item.duration, item.id, removeToast])

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
          setExiting(true)
          finishTimerReference.current = window.setTimeout(
            () => removeToast(item.id),
            ANIM_DURATION
          )
        }, remainingReference.current)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hovering, exiting])

  const handleClose = useCallback((): void => {
    if (exiting) return
    if (autoTimerReference.current) {
      clearTimeout(autoTimerReference.current)
      autoTimerReference.current = null
    }
    setExiting(true)
    finishTimerReference.current = window.setTimeout(
      () => removeToast(item.id),
      ANIM_DURATION
    )
  }, [exiting, item.id, removeToast])

  const handleMouseEnter = useCallback(() => setHovering(true), [])
  const handleMouseLeave = useCallback(() => setHovering(false), [])

  const statusClass =
    item.status === 'success'
      ? 'statusSuccess'
      : item.status === 'failure'
        ? 'statusFailure'
        : 'statusWarning'

  return {
    hovering,
    exiting,
    handleMouseEnter,
    handleMouseLeave,
    handleClose,
    statusClass
  }
}
