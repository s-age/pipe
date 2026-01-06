import type React from 'react'
import { useSyncExternalStore } from 'react'

export type ConfirmDescriptor = {
  props: {
    message?: string
    title?: string
    onCancel?: () => void
    onConfirm?: () => Promise<void> | void
  }
  type: 'confirm'
}

export type ModalEventData = {
  content?: React.ReactNode | ConfirmDescriptor
  id?: number | string
  options?: Record<string, unknown>
}

export type ModalEntry = {
  content: React.ReactNode | ConfirmDescriptor | null
  id: number | string
}

let stack: ModalEntry[] = []
const listeners: Set<() => void> = new Set()

const getStack = (): ModalEntry[] => stack

const subscribe = (callback: () => void): (() => void) => {
  listeners.add(callback)

  return () => listeners.delete(callback)
}

const notify = (): void => listeners.forEach((l) => l())

let idSeed = 1
const genId = (): number => idSeed++

export const showModal = (data: ModalEventData): number | string => {
  const id = data.id !== undefined ? data.id : genId()
  const entry: ModalEntry = { id, content: data.content ?? null }
  stack = [...stack, entry]
  notify()

  return id
}

export const hideModal = (id?: number | string): void => {
  if (id == null) {
    stack = stack.slice(0, -1)
    notify()

    return
  }

  const sid = id
  stack = stack.filter((event) => event.id !== sid)
  notify()
}

export const clearModals = (): void => {
  stack = []
  notify()
}

export const useModalStore = (): {
  stack: ModalEntry[]
  clearModals: () => void
  hideModal: (id?: number | string) => void
  showModal: (data: ModalEventData) => number | string
} => {
  const snapshot = useSyncExternalStore(subscribe, getStack, getStack)

  return {
    stack: snapshot,
    showModal,
    hideModal,
    clearModals
  }
}
