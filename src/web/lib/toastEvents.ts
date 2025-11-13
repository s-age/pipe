import { eventBus } from './eventBus'

export type ToastEventData = {
  status: 'success' | 'failure' | 'warning'
  title?: string
  description?: string
  position?:
    | 'top-left'
    | 'top-center'
    | 'top-right'
    | 'bottom-left'
    | 'bottom-center'
    | 'bottom-right'
  duration?: number | null
}

const TOAST_EVENT = 'toast:show'

export const emitToast = {
  success: (titleOrData: string | Partial<ToastEventData>): void => {
    const data: ToastEventData =
      typeof titleOrData === 'string'
        ? { status: 'success', title: titleOrData }
        : { status: 'success', ...titleOrData }
    eventBus.emit(TOAST_EVENT, data)
  },

  failure: (titleOrData: string | Partial<ToastEventData>): void => {
    const data: ToastEventData =
      typeof titleOrData === 'string'
        ? { status: 'failure', title: titleOrData }
        : { status: 'failure', ...titleOrData }
    eventBus.emit(TOAST_EVENT, data)
  },

  warning: (titleOrData: string | Partial<ToastEventData>): void => {
    const data: ToastEventData =
      typeof titleOrData === 'string'
        ? { status: 'warning', title: titleOrData }
        : { status: 'warning', ...titleOrData }
    eventBus.emit(TOAST_EVENT, data)
  },

  show: (data: ToastEventData): void => {
    eventBus.emit(TOAST_EVENT, data)
  }
}

export const onToastEvent = (callback: (data: ToastEventData) => void): (() => void) =>
  eventBus.on<ToastEventData>(TOAST_EVENT, callback)
