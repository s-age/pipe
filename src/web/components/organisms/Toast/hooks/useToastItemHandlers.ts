import { useCallback, useState } from 'react'

import type { ToastItem as ToastItemType } from '@/stores/useAppStore'

import { useToastItemLifecycle } from './useToastItemLifecycle'

const ANIM_DURATION = 180

type UseToastItemHandlersProperties = {
  item: ToastItemType
  removeToast: (id: string) => void
}

export const useToastItemHandlers = ({
  item,
  removeToast
}: UseToastItemHandlersProperties): {
  exiting: boolean
  hovering: boolean
  statusClass: 'statusSuccess' | 'statusFailure' | 'statusWarning'
  handleClose: () => void
  handleMouseEnter: () => void
  handleMouseLeave: () => void
} => {
  const [hovering, setHovering] = useState(false)
  const [exiting, setExiting] = useState(false)

  const handleExit = useCallback((): void => {
    setExiting(true)
    setTimeout(() => removeToast(item.id), ANIM_DURATION)
  }, [item.id, removeToast])

  // Use lifecycle hook
  useToastItemLifecycle({
    item,
    hovering,
    exiting,
    onExit: handleExit
  })

  const handleClose = useCallback((): void => {
    if (exiting) return
    handleExit()
  }, [exiting, handleExit])

  const handleMouseEnter = useCallback(() => setHovering(true), [])
  const handleMouseLeave = useCallback(() => setHovering(false), [])

  const statusClass =
    item.status === 'success'
      ? 'statusSuccess'
      : item.status === 'failure'
        ? 'statusFailure'
        : 'statusWarning'

  return {
    hovering,
    exiting,
    handleMouseEnter,
    handleMouseLeave,
    handleClose,
    statusClass
  }
}
