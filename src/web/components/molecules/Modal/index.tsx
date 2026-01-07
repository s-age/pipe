import type { JSX } from 'react'
import React from 'react'
import { createPortal } from 'react-dom'

import { Box } from '@/components/molecules/Box'
import { themeClass } from '@/styles/theme.css'

import { useModalHandlers } from './hooks/useModalHandlers'
import * as styles from './style.css'

// Module-level modal root creation. Keep it at module scope so it's created
// once when the module is imported (avoids reading refs during render).
const MODAL_ROOT_ID = 'modal-root'

let modalRoot =
  typeof document !== 'undefined'
    ? (document.getElementById(MODAL_ROOT_ID) as HTMLElement | null)
    : null
if (typeof document !== 'undefined' && !modalRoot) {
  modalRoot = document.createElement('div')
  modalRoot.id = MODAL_ROOT_ID
  modalRoot.className = themeClass
  document.body.appendChild(modalRoot)
}

export const getModalRoot = (): HTMLElement | null => modalRoot

type ModalProperties = {
  /** Whether the modal is open (controlled by parent) */
  isOpen: boolean
  children?: React.ReactNode
  onClose?: () => void
}

/**
 * Modal - Molecule Component
 *
 * Pure presentation Modal UI. Renders via Portal.
 * Follows molecules.md pattern: Local UI state managed via props.
 *
 * @example
 * <Modal isOpen={isOpen} onClose={handleClose}>
 *   <h1>Title</h1>
 *   <p>Content</p>
 * </Modal>
 */
export const Modal = ({
  isOpen,
  children,
  onClose
}: ModalProperties): JSX.Element | null => {
  const modalRoot = getModalRoot()
  const { onContentMouseDown, onOverlayMouseDown } = useModalHandlers(isOpen, onClose)

  if (!isOpen || !modalRoot) return null

  return createPortal(
    <Box
      className={styles.overlay}
      onMouseDown={onOverlayMouseDown}
      role="dialog"
      aria-modal="true"
    >
      <Box className={styles.content} onMouseDown={onContentMouseDown}>
        {children}
      </Box>
    </Box>,
    modalRoot
  )
}
