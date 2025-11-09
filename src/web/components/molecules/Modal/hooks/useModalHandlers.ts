import { useCallback, useEffect } from 'react'

export const useModalHandlers = (
  open: boolean,
  onClose?: () => void,
): {
  onOverlayMouseDown: (event: React.MouseEvent<HTMLDivElement>) => void
  onContentMouseDown: (event: React.MouseEvent<HTMLDivElement>) => void
} => {
  const onOverlayMouseDown = useCallback(
    (event: React.MouseEvent<HTMLDivElement>): void => {
      if (event.target === event.currentTarget) onClose?.()
    },
    [onClose],
  )

  const onContentMouseDown = useCallback(
    (event: React.MouseEvent<HTMLDivElement>): void => {
      event.stopPropagation()
    },
    [],
  )

  useEffect(() => {
    if (!open) return
    const onKey = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') onClose?.()
    }
    document.addEventListener('keydown', onKey)

    return (): void => document.removeEventListener('keydown', onKey)
  }, [open, onClose])

  return { onOverlayMouseDown, onContentMouseDown }
}

// prefer named exports (already a named export above)
