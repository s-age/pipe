import { useCallback } from 'react'

import { useModalLifecycle } from './useModalLifecycle'

/**
 * useModalHandlers
 *
 * Handles Modal UI events (Overlay click).
 * Pattern: Handlers (separated from Lifecycle per hooks.md)
 *
 * @param isOpen - Whether modal is currently open
 * @param onClose - Callback to close modal (injected by parent)
 */
export const useModalHandlers = (
  isOpen: boolean,
  onClose?: () => void
): {
  onContentMouseDown: (event: React.MouseEvent<HTMLDivElement>) => void
  onOverlayMouseDown: (event: React.MouseEvent<HTMLDivElement>) => void
} => {
  // Handler: Close on overlay click
  const onOverlayMouseDown = useCallback(
    (event: React.MouseEvent<HTMLDivElement>): void => {
      if (event.target === event.currentTarget) onClose?.()
    },
    [onClose]
  )

  // Handler: Prevent propagation on content click
  const onContentMouseDown = useCallback(
    (event: React.MouseEvent<HTMLDivElement>): void => {
      event.stopPropagation()
    },
    []
  )

  // Lifecycle: Escape key listener
  useModalLifecycle({ isOpen, onClose })

  return { onOverlayMouseDown, onContentMouseDown }
}
