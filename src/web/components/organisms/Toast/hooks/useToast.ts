import type { ToastItem } from '../../../../stores/useToastStore'
import { useToastStore } from '../../../../stores/useToastStore'

export type ToastInput = Partial<Omit<ToastItem, 'id' | 'createdAt'>>

export const useToast = (): {
  toasts: ToastItem[]
  addToast: (toast: Omit<ToastItem, 'id' | 'createdAt'>) => string
  removeToast: (id: string) => void
  clearToasts: () => void
  show: (data: string | ToastInput) => string
  success: (data: string | ToastInput) => string
  failure: (data: string | ToastInput) => string
  warning: (data: string | ToastInput) => string
} => {
  const store = useToastStore()

  const show = (data: string | ToastInput): string => {
    const payload: ToastInput = typeof data === 'string' ? { title: data } : data

    return store.addToast(payload as Omit<ToastItem, 'id' | 'createdAt'>)
  }

  const success = (data: string | ToastInput): string =>
    show(
      typeof data === 'string'
        ? { title: data, status: 'success' }
        : { ...data, status: 'success' }
    )

  const failure = (data: string | ToastInput): string =>
    show(
      typeof data === 'string'
        ? { title: data, status: 'failure' }
        : { ...data, status: 'failure' }
    )

  const warning = (data: string | ToastInput): string =>
    show(
      typeof data === 'string'
        ? { title: data, status: 'warning' }
        : { ...data, status: 'warning' }
    )

  return {
    toasts: store.toasts,
    addToast: store.addToast,
    removeToast: store.removeToast,
    clearToasts: store.clearToasts,
    show,
    success,
    failure,
    warning
  }
}
