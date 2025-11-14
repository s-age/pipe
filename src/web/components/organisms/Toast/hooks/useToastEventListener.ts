import { useCallback, useEffect, useState } from 'react'

import { onToastEvent } from '@/lib/toastEvents'
import type { ToastEventData } from '@/lib/toastEvents'
import type { ToastPosition, ToastStatus } from '@/stores/useAppStore'

export type ToastItem = {
  id: string
  status: ToastStatus
  position?: ToastPosition
  title?: string
  description?: string
  duration?: number | null
  dismissible?: boolean
  createdAt: number
}

let idCounter = 0
const genId = (): string => {
  idCounter += 1

  return `toast-${Date.now()}-${idCounter}`
}

export const useToastEventListener = (): {
  toasts: ToastItem[]
  removeToast: (id: string) => void
} => {
  const [toasts, setToasts] = useState<ToastItem[]>([])

  const removeToast = useCallback((id: string) => {
    setToasts((previous) => previous.filter((t) => t.id !== id))
  }, [])

  useEffect(() => {
    const unsubscribe = onToastEvent((data: ToastEventData) => {
      const item: ToastItem = {
        id: genId(),
        createdAt: Date.now(),
        duration: 5000,
        dismissible: true,
        ...data
      }
      setToasts((previous) => [...previous, item])
    })

    return unsubscribe
  }, [])

  return { toasts, removeToast }
}
