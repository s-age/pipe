import { eventBus } from './eventBus'

export type ModalEventData = {
  id?: number | string
  content?: React.ReactNode
  options?: Record<string, unknown>
}

const MODAL_EVENT = 'modal:show'
const MODAL_HIDE = 'modal:hide'

export const emitModal = {
  show: (data: ModalEventData): void => {
    eventBus.emit(MODAL_EVENT, data)
  },
  hide: (id?: number | string): void => {
    eventBus.emit(MODAL_HIDE, { id })
  }
}

export const onModalShow = (callback: (data: ModalEventData) => void): (() => void) =>
  eventBus.on(MODAL_EVENT, callback)

export const onModalHide = (
  callback: (data: { id?: number | string }) => void
): (() => void) => eventBus.on(MODAL_HIDE, callback)
