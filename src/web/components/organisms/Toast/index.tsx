import type { JSX } from 'react'
import { useEffect, useMemo, useRef, useState } from 'react'

import { useAppStore } from '@/stores/useAppStore'
import type { ToastItem as ToastItemType } from '@/stores/useAppStore'

import * as styles from './style.css'

type Position =
  | 'top-left'
  | 'top-center'
  | 'top-right'
  | 'bottom-left'
  | 'bottom-center'
  | 'bottom-right'

const allPositions: Position[] = [
  'top-left',
  'top-center',
  'top-right',
  'bottom-left',
  'bottom-center',
  'bottom-right',
]

const Icon = ({ status }: { status: string }): JSX.Element => {
  if (status === 'success') return <span className={styles.icon}>✓</span>
  if (status === 'failure') return <span className={styles.icon}>✕</span>

  return <span className={styles.icon}>!</span>
}

const ToastItem = ({ item }: { item: ToastItemType }): JSX.Element => {
  const { removeToast } = useAppStore()
  const autoTimerReference = useRef<number | null>(null)
  const finishTimerReference = useRef<number | null>(null)
  const startAtReference = useRef<number | null>(null)
  const remainingReference = useRef<number | null>(item.duration ?? null)
  const [hovering, setHovering] = useState(false)
  const [exiting, setExiting] = useState(false)

  const ANIM_DURATION = 180

  useEffect(() => {
    // initialize remaining
    remainingReference.current = item.duration ?? null

    const startTimer = (ms: number): void => {
      startAtReference.current = Date.now()
      autoTimerReference.current = window.setTimeout(() => {
        // start exit animation
        setExiting(true)
        finishTimerReference.current = window.setTimeout(
          () => removeToast(item.id),
          ANIM_DURATION,
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
      // pause
      if (autoTimerReference.current && startAtReference.current) {
        const elapsed = Date.now() - startAtReference.current
        remainingReference.current = Math.max(
          0,
          (remainingReference.current ?? 0) - elapsed,
        )
        clearTimeout(autoTimerReference.current)
        autoTimerReference.current = null
      }
    } else {
      // resume
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
            ANIM_DURATION,
          )
        }, remainingReference.current)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hovering, exiting])

  const handleClose = (): void => {
    if (exiting) return
    if (autoTimerReference.current) {
      clearTimeout(autoTimerReference.current)
      autoTimerReference.current = null
    }
    setExiting(true)
    finishTimerReference.current = window.setTimeout(
      () => removeToast(item.id),
      ANIM_DURATION,
    )
  }

  const statusClass =
    item.status === 'success'
      ? styles.statusSuccess
      : item.status === 'failure'
        ? styles.statusFailure
        : styles.statusWarning

  return (
    <div
      role={item.status === 'failure' ? 'alert' : 'status'}
      aria-live={item.status === 'failure' ? 'assertive' : 'polite'}
      className={`${styles.toast} ${exiting ? styles.exit : styles.enter} ${statusClass}`}
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
    >
      <div className={styles.row}>
        <Icon status={item.status} />
        <div className={styles.content}>
          {item.title ? <div className={styles.title}>{item.title}</div> : null}
          {item.description ? (
            <div className={styles.description}>{item.description}</div>
          ) : null}
        </div>
        {item.dismissible ? (
          <button className={styles.close} onClick={handleClose} aria-label="Close">
            ×
          </button>
        ) : null}
      </div>
    </div>
  )
}

const Toasts = (): JSX.Element => {
  const { state } = useAppStore()

  const grouped = useMemo<Record<string, ToastItemType[]>>(() => {
    const map: Record<string, ToastItemType[]> = {}
    for (const p of allPositions) map[p] = []
    for (const t of state.toasts) {
      const pos = t.position ?? 'top-right'
      if (!map[pos]) map[pos] = []
      map[pos].push(t)
    }

    return map
  }, [state.toasts])

  return (
    <>
      {allPositions.map(
        (pos: Position): JSX.Element => (
          <div key={pos} className={styles.container} data-pos={pos} data-posname={pos}>
            {grouped[pos].map(
              (item): JSX.Element => (
                <ToastItem key={item.id} item={item} />
              ),
            )}
          </div>
        ),
      )}
    </>
  )
}

export default Toasts
