import React from 'react'

import { showModal, hideModal, type ConfirmDescriptor } from '@/stores/useModalStore'

let modalIdCounter = 1

/**
 * useModal
 *
 * Public Facade for Modal System.
 * Pattern: Integration Hook (Exception per hooks.md - Store consumer hook)
 *
 * Exported for Pages/Organisms to trigger modals programmatically.
 *
 * @example
 * const { show, hide } = useModal()
 * const id = show(<div>Content</div>)
 * hide(id)
 */
export const useModal = (): {
  show: (content: React.ReactNode | ConfirmDescriptor, id?: number) => number
  hide: (id?: number | string) => void
} => {
  const show = React.useCallback(
    (content: React.ReactNode | ConfirmDescriptor, id?: number): number => {
      const assignedId = typeof id === 'number' ? id : modalIdCounter++
      // We always return a numeric id from this hook for compatibility with callers
      showModal({ id: assignedId, content })

      return assignedId
    },
    []
  )

  const hide = React.useCallback((id?: number | string): void => {
    hideModal(id)
  }, [])

  return { show, hide }
}
