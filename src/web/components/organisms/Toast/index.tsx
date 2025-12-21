import { clsx } from 'clsx'
import type { JSX } from 'react'
import { createPortal } from 'react-dom'

import type { ToastItem } from '@/stores/useToastStore'

import { useToast } from './hooks/useToast'
import { useToastHandlers } from './hooks/useToastHandlers'
import { useToastItemHandlers } from './hooks/useToastItemHandlers'
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
  'bottom-right'
]

const Icon = ({ status }: { status: ToastItem['status'] }): JSX.Element => {
  if (status === 'success') return <span className={styles.icon}>✓</span>
  if (status === 'failure') return <span className={styles.icon}>✕</span>

  return <span className={styles.icon}>!</span>
}

const statusClassMap: Record<ToastItem['status'], string> = {
  success: styles.statusSuccess,
  failure: styles.statusFailure,
  warning: styles.statusWarning
}

const ToastItem = ({
  item,
  removeToast
}: {
  item: ToastItem
  removeToast: (id: string) => void
}): JSX.Element => {
  const { handleMouseEnter, handleMouseLeave, handleClose, exiting } =
    useToastItemHandlers({ item, removeToast })

  return (
    <div
      role={item.status === 'failure' ? 'alert' : 'status'}
      aria-live={item.status === 'failure' ? 'assertive' : 'polite'}
      className={clsx(
        styles.toast,
        exiting ? styles.exit : styles.enter,
        statusClassMap[item.status]
      )}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
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

export const Toasts = (): JSX.Element => {
  const { toasts, removeToast } = useToast()
  const { grouped } = useToastHandlers(toasts)

  return createPortal(
    allPositions.map((pos) => (
      <div key={pos} className={styles.container} data-pos={pos}>
        {grouped[pos].map((item) => (
          <ToastItem key={item.id} item={item} removeToast={removeToast} />
        ))}
      </div>
    )),
    document.body
  )
}
