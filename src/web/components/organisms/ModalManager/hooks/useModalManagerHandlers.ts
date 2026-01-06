import { useCallback } from 'react'

import type { ModalEntry, ConfirmDescriptor } from '@/stores/useModalStore'
import { useModalStore } from '@/stores/useModalStore'

/**
 * useModalManagerHandlers
 *
 * Business Logic for ModalManager.
 * Pattern: Handlers (Connects to Store, manages modal lifecycle)
 *
 * @returns stack - Array of modal entries from store
 * @returns handleClose - Function to close modal by ID
 * @returns createCloseHandler - Factory function to create close handler for specific modal ID
 * @returns isConfirmDescriptor - Type guard for ConfirmDescriptor
 */
export const useModalManagerHandlers = (): {
  stack: ModalEntry[]
  createCloseHandler: (id: number | string) => () => void
  handleClose: (id: number | string) => void
  isConfirmDescriptor: (v: unknown) => v is ConfirmDescriptor
} => {
  const { hideModal, stack } = useModalStore()

  const handleClose = useCallback(
    (id: number | string): void => {
      hideModal(id)
    },
    [hideModal]
  )

  const createCloseHandler = useCallback(
    (id: number | string) => (): void => {
      hideModal(id)
    },
    [hideModal]
  )

  const isConfirmDescriptor = (v: unknown): v is ConfirmDescriptor =>
    typeof v === 'object' && v !== null && (v as { type?: unknown }).type === 'confirm'

  return { stack, handleClose, createCloseHandler, isConfirmDescriptor }
}
