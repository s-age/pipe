import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Heading } from '@/components/atoms/Heading'
// ConfirmModal no longer renders its own Modal wrapper.
// The ModalProvider is responsible for rendering a Modal around
// any modal content provided via the `show` API.

import * as styles from './style.css'

type ConfirmModalProperties = {
  title: string
  message: string
  icon?: React.ReactNode
  onConfirm: () => void
  onCancel: () => void
  confirmText?: string
  cancelText?: string
}

// ConfirmModal now returns the inner content only.
// It is intended to be passed to the ModalProvider's `show` API,
// which will render the surrounding Modal.
export const ConfirmModal = ({
  title,
  message,
  icon,
  onConfirm,
  onCancel,
  confirmText = 'OK',
  cancelText = 'Cancel'
}: ConfirmModalProperties): JSX.Element => (
  <div className={styles.container}>
    <div className={styles.header}>
      {icon && <div className={styles.icon}>{icon}</div>}
      <Heading level={3} className={styles.title}>
        {title}
      </Heading>
    </div>
    <p className={styles.message}>{message}</p>
    <div className={styles.actions}>
      <Button type="button" onClick={onCancel} className="primary">
        {' '}
        {cancelText}
      </Button>
      <Button type="button" onClick={onConfirm} className="secondary">
        {confirmText}
      </Button>
    </div>
  </div>
)
