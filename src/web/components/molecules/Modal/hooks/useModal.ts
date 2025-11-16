import React from 'react'

import { emitModal } from '@/lib/modalEvents'

let modalIdCounter = 1

export const useModal = (): {
  show: (content: React.ReactNode, id?: number) => number
  hide: (id?: number) => void
} => {
  const show = React.useCallback((content: React.ReactNode, id?: number): number => {
    const assignedId = typeof id === 'number' ? id : modalIdCounter++
    emitModal.show({ id: assignedId, content })

    return assignedId
  }, [])

  const hide = React.useCallback((id?: number): void => {
    emitModal.hide(id)
  }, [])

  return { show, hide }
}
