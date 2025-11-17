import type { JSX } from 'react'
import React, { useCallback } from 'react'
import { createPortal } from 'react-dom'

import { useModalStore } from '@/stores/useModalStore'

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

// ModalManager: render the modal stack from the modal store
type StoreModalEntry = {
  id: number | string
  content: React.ReactNode | null
}

export const ModalManager = (): JSX.Element | null => {
  const store = useModalStore()
  const stack = store.stack

  const removeById = useCallback(
    (id: string | number): void => {
      store.hideModal(id)
    },
    [store]
  )

  const ModalItem = ({ entry }: { entry: StoreModalEntry }): JSX.Element => {
    const handleClose = useCallback(() => removeById(entry.id), [entry.id])

    return (
      <Modal key={String(entry.id)} open={true} onClose={handleClose}>
        {entry.content}
      </Modal>
    )
  }

  if (typeof document === 'undefined') return null

  return createPortal(
    <>
      {stack.map((entry) => (
        <ModalItem key={String(entry.id)} entry={entry} />
      ))}
    </>,
    document.body
  )
}
