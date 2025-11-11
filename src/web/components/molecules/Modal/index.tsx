import type { JSX } from 'react'
import React from 'react'
import { createPortal } from 'react-dom'

import { getModalRoot, useModalHandlers } from './hooks/useModalHandlers'
import * as styles from './style.css'

type ModalProperties = {
  open: boolean
  onClose?: () => void
  children?: React.ReactNode
}

export const Modal = ({
  open,
  onClose,
  children
}: ModalProperties): JSX.Element | null => {
  const modalRoot = getModalRoot()

  const { onOverlayMouseDown, onContentMouseDown } = useModalHandlers(open, onClose)

  if (!open || !modalRoot) return null

  return createPortal(
    <div className={styles.overlay} onMouseDown={onOverlayMouseDown}>
      <div className={styles.content} onMouseDown={onContentMouseDown}>
        {children}
      </div>
    </div>,
    modalRoot
  )
}
