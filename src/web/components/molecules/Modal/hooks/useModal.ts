import React from 'react'

import { showModal, hideModal } from '@/stores/useModalStore'

let modalIdCounter = 1

export const useModal = (): {
  show: (content: React.ReactNode, id?: number) => number
  hide: (id?: number | string) => void
} => {
  const show = React.useCallback((content: React.ReactNode, id?: number): number => {
    const assignedId = typeof id === 'number' ? id : modalIdCounter++
    // We always return a numeric id from this hook for compatibility with callers
    showModal({ id: assignedId, content })

    return assignedId
  }, [])

  const hide = React.useCallback((id?: number | string): void => {
    hideModal(id)
  }, [])

  return { show, hide }
}
