import type { JSX } from 'react'

import { useAppStore } from '@/stores/useAppStore'

import * as styles from './style.css'

export const LoadingOverlay = (): JSX.Element | null => {
  const { isLoading } = useAppStore()

  if (!isLoading) return null

  return (
    <div
      className={styles.overlay}
      role="status"
      aria-live="polite"
      aria-label="Loading"
    >
      <div className={styles.spinner} aria-hidden />
      <span className={styles.visuallyHidden}>Loading</span>
    </div>
  )
}
