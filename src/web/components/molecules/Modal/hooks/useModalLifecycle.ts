import { useEffect } from 'react'

export type UseModalLifecycleProperties = {
  isOpen: boolean
  onClose?: () => void
}

/**
 * useModalLifecycle
 *
 * Manages Modal lifecycle effects (Escape key listener).
 * Pattern: Lifecycle (separated from Handlers per hooks.md)
 *
 * Note: Per hooks.md:28, small components may include simple lifecycle
 * effects within Handlers. However, this has been extracted for consistency.
 */
export const useModalLifecycle = ({
  isOpen,
  onClose
}: UseModalLifecycleProperties): void => {
  // Lifecycle: Escape key listener
  useEffect(() => {
    if (!isOpen) return
    const onKey = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') onClose?.()
    }
    document.addEventListener('keydown', onKey)

    return (): void => document.removeEventListener('keydown', onKey)
  }, [isOpen, onClose])
}
