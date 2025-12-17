import { useCallback, useEffect } from 'react'

/**
 * useModalHandlers
 *
 * Handles Modal UI events (Overlay click, Escape key).
 * Pattern: Handlers (with internal Lifecycle for small component - per hooks.md:28)
 *
 * @param isOpen - Whether modal is currently open
 * @param onClose - Callback to close modal (injected by parent)
 */
export const useModalHandlers = (
  isOpen: boolean,
  onClose?: () => void
): {
  onOverlayMouseDown: (event: React.MouseEvent<HTMLDivElement>) => void
  onContentMouseDown: (event: React.MouseEvent<HTMLDivElement>) => void
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

  // Lifecycle: Escape key listener (internal effect, acceptable per hooks.md:28)
  useEffect(() => {
    if (!isOpen) return
    const onKey = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') onClose?.()
    }
    document.addEventListener('keydown', onKey)

    return (): void => document.removeEventListener('keydown', onKey)
  }, [isOpen, onClose])

  return { onOverlayMouseDown, onContentMouseDown }
}
