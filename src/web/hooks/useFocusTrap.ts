import { useEffect, useRef } from 'react'

export type UseFocusTrapProperties = {
  isOpen: boolean
}

/**
 * useFocusTrap
 *
 * Manages focus trap within modal and focus restoration.
 * Pattern: Lifecycle (accessibility feature)
 *
 * - Saves focus before modal opens
 * - Traps focus within modal when open
 * - Restores focus when modal closes
 */
export const useFocusTrap = ({ isOpen }: UseFocusTrapProperties): void => {
  const previousActiveElement = useRef<HTMLElement | null>(null)

  useEffect(() => {
    if (!isOpen) return

    // Save current active element
    previousActiveElement.current = document.activeElement as HTMLElement

    // Get modal root
    const modalRoot = document.getElementById('modal-root')
    if (!modalRoot) return

    // Focus first focusable element in modal
    const focusableElements = modalRoot.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    const firstFocusable = focusableElements[0]
    if (firstFocusable) {
      firstFocusable.focus()
    }

    // Trap focus within modal
    const handleKeyDown = (event: KeyboardEvent): void => {
      if (event.key !== 'Tab') return

      const focusableElements = modalRoot.querySelectorAll<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      const firstElement = focusableElements[0]
      const lastElement = focusableElements[focusableElements.length - 1]

      if (event.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          event.preventDefault()
          lastElement?.focus()
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          event.preventDefault()
          firstElement?.focus()
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)

    // Cleanup: restore focus when modal closes
    return (): void => {
      document.removeEventListener('keydown', handleKeyDown)
      previousActiveElement.current?.focus()
      previousActiveElement.current = null
    }
  }, [isOpen])
}
