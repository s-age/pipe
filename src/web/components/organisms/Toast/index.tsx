import type { JSX } from 'react'
import {} from 'react'

import { useAppStore } from '@/stores/useAppStore'
import type { ToastItem as ToastItemType } from '@/stores/useAppStore'

import { useGroupedToasts } from './hooks/useGroupedToasts'
import { useToastItem } from './hooks/useToastItem'
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

const Icon = ({ status }: { status: string }): JSX.Element => {
  if (status === 'success') return <span className={styles.icon}>✓</span>
  if (status === 'failure') return <span className={styles.icon}>✕</span>

  return <span className={styles.icon}>!</span>
}

const ToastItem = ({ item }: { item: ToastItemType }): JSX.Element => {
  const { removeToast } = useAppStore()

  const { handleMouseEnter, handleMouseLeave, handleClose, exiting, statusClass } =
    useToastItem(item, removeToast)

  const statusClassName =
    statusClass === 'statusSuccess'
      ? styles.statusSuccess
      : statusClass === 'statusFailure'
        ? styles.statusFailure
        : styles.statusWarning

  return (
    <div
      role={item.status === 'failure' ? 'alert' : 'status'}
      aria-live={item.status === 'failure' ? 'assertive' : 'polite'}
      className={`${styles.toast} ${exiting ? styles.exit : styles.enter} ${statusClassName}`}
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
  const { grouped } = useGroupedToasts()

  const positionElements: JSX.Element[] = []
  for (const pos of allPositions) {
    const children: JSX.Element[] = []
    for (const item of grouped[pos]) {
      children.push(<ToastItem key={item.id} item={item} />)
    }
    positionElements.push(
      <div key={pos} className={styles.container} data-pos={pos} data-posname={pos}>
        {children}
      </div>
    )
  }

  return <>{positionElements}</>
}

// Default export removed — use named export `Toasts`
