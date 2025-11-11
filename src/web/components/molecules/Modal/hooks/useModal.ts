import React from 'react'

import { useModalContext } from '@/stores/useModalStore'

export const useModal = (): {
  show: (content: React.ReactNode) => number
  hide: (id?: number) => void
} => {
  const context = useModalContext()

  const show = React.useCallback(
    (content: React.ReactNode): number => context.show(content),
    [context]
  )

  const hide = React.useCallback((id?: number): void => context.hide(id), [context])

  return { show, hide }
}
