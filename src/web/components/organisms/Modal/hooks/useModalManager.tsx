import React, { useCallback } from 'react'
import type { JSX } from 'react'
import { createPortal } from 'react-dom'

import { ConfirmModal } from '@/components/molecules/ConfirmModal'
import {
  useModalStore,
  type ModalEntry,
  type ConfirmDescriptor
} from '@/stores/useModalStore'

import { getModalRoot, useModalHandlers } from '../hooks/useModalHandlers'
// eslint-disable-next-line no-restricted-imports
import * as styles from '../style.css'

// ModalManager: render the modal stack from the modal store
export const ModalManager = (): JSX.Element | null => {
  const store = useModalStore()
  const stack = store.stack

  const removeById = useCallback(
    (id: string | number): void => {
      store.hideModal(id)
    },
    [store]
  )

  const isConfirmDescriptor = (v: unknown): v is ConfirmDescriptor =>
    typeof v === 'object' && v !== null && (v as { type?: unknown }).type === 'confirm'

  const ModalItem = ({ entry }: { entry: ModalEntry }): JSX.Element | null => {
    const handleClose = useCallback(() => removeById(entry.id), [entry.id])

    const modalRoot = getModalRoot()
    const { onOverlayMouseDown, onContentMouseDown } = useModalHandlers(
      true,
      handleClose
    )

    const content = entry.content

    let innerJSX: React.ReactNode | null = null
    if (isConfirmDescriptor(content)) {
      const desc = content as ConfirmDescriptor
      innerJSX = (
        <ConfirmModal
          title={desc.props.title ?? ''}
          message={desc.props.message ?? ''}
          onConfirm={desc.props.onConfirm ?? ((): void => undefined)}
          onCancel={desc.props.onCancel ?? ((): void => undefined)}
        />
      )
    } else if (content != null && !isConfirmDescriptor(content)) {
      innerJSX = content as React.ReactNode
    }

    if (!modalRoot || innerJSX == null) return null

    return createPortal(
      <div
        key={String(entry.id)}
        className={styles.overlay}
        onMouseDown={onOverlayMouseDown}
      >
        <div className={styles.content} onMouseDown={onContentMouseDown}>
          {innerJSX}
        </div>
      </div>,
      modalRoot
    )
  }

  if (typeof document === 'undefined') return null

  return (
    <>
      {stack.map((entry) => (
        <ModalItem key={String(entry.id)} entry={entry} />
      ))}
    </>
  )
}

// Use named export only
