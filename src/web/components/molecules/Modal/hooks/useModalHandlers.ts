import { useCallback, useEffect } from 'react'

// Module-level modal root creation. Keep it at module scope so it's created
// once when the module is imported (avoids reading refs during render).
const MODAL_ROOT_ID = 'modal-root'

let modalRoot = document.getElementById(MODAL_ROOT_ID) as HTMLElement | null
if (!modalRoot) {
  modalRoot = document.createElement('div')
  modalRoot.id = MODAL_ROOT_ID
  document.body.appendChild(modalRoot)
}

export const getModalRoot = (): HTMLElement | null => modalRoot

export const useModalHandlers = (
  open: boolean,
  onClose?: () => void
): {
  onOverlayMouseDown: (event: React.MouseEvent<HTMLDivElement>) => void
  onContentMouseDown: (event: React.MouseEvent<HTMLDivElement>) => void
} => {
  const onOverlayMouseDown = useCallback(
    (event: React.MouseEvent<HTMLDivElement>): void => {
      if (event.target === event.currentTarget) onClose?.()
    },
    [onClose]
  )

  const onContentMouseDown = useCallback(
    (event: React.MouseEvent<HTMLDivElement>): void => {
      event.stopPropagation()
    },
    []
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
