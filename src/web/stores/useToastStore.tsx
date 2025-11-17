import { useSyncExternalStore } from 'react'

export type ToastStatus = 'success' | 'failure' | 'warning'
export type ToastPosition =
  | 'top-left'
  | 'top-center'
  | 'top-right'
  | 'bottom-left'
  | 'bottom-center'
  | 'bottom-right'

export type ToastItem = {
  id: string
  status: ToastStatus
  title?: string
  description?: string
  position?: ToastPosition
  duration?: number | null
  dismissible?: boolean
  createdAt: number
}

const listeners: Set<() => void> = new Set()
let toasts: ToastItem[] = []
let idCounter = 0

const genId = (): string => {
  idCounter += 1

  return `toast-${Date.now()}-${idCounter}`
}

const notify = (): void => {
  listeners.forEach((l) => l())
}

export const getToasts = (): ToastItem[] => toasts

export const subscribe = (callback: () => void): (() => void) => {
  listeners.add(callback)

  return (): void => {
    listeners.delete(callback)
  }
}

export const addToast = (data: Omit<ToastItem, 'id' | 'createdAt'>): string => {
  const id = genId()
  const item: ToastItem = {
    id,
    createdAt: Date.now(),
    duration: 5000,
    dismissible: true,
    ...data
  }
  toasts = [...toasts, item]
  notify()

  // Auto-dismiss if duration is set
  if (item.duration && item.duration > 0) {
    setTimeout(() => {
      removeToast(id)
    }, item.duration)
  }

  return id
}

export const removeToast = (id: string): void => {
  const previous = toasts
  toasts = previous.filter((t) => t.id !== id)
  if (toasts.length !== previous.length) notify()
}

export const clearToasts = (): void => {
  toasts = []
  notify()
}

// Hook for components to consume toasts via useSyncExternalStore
export const useToastStore = (): {
  toasts: ToastItem[]
  addToast: (data: Omit<ToastItem, 'id' | 'createdAt'>) => string
  removeToast: (id: string) => void
  clearToasts: () => void
} => {
  const snapshot = useSyncExternalStore(subscribe, getToasts, getToasts)

  return {
    toasts: snapshot,
    addToast,
    removeToast,
    clearToasts
  }
}
