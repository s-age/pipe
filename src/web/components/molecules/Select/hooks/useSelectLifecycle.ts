import { useEffect, useRef } from 'react'

type UseSelectLifecycleProperties = {
  isOpen: boolean
  clearHighlight: () => void
  close: () => void
}

export const useSelectLifecycle = ({
  isOpen,
  clearHighlight,
  close
}: UseSelectLifecycleProperties): {
  rootReference: React.RefObject<HTMLDivElement | null>
} => {
  const rootReference = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!isOpen) return

    const handlePointerDown = (event: Event): void => {
      if (
        rootReference.current &&
        !rootReference.current.contains(event.target as Node)
      ) {
        close()
        clearHighlight()
      }
    }

    document.addEventListener('pointerdown', handlePointerDown as EventListener)

    return (): void => {
      document.removeEventListener('pointerdown', handlePointerDown as EventListener)
    }
  }, [isOpen, close, clearHighlight])

  return { rootReference }
}

// (Removed temporary default export) Use named export `useSelectLifecycle`.
