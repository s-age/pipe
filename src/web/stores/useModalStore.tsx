import React from 'react'
import { useSyncExternalStore } from 'react'
import type { JSX } from 'react'

import { ModalManager } from '@/components/organisms/Modal'

export type ConfirmDescriptor = {
  type: 'confirm'
  props: {
    title?: string
    message?: string
    onConfirm?: () => Promise<void> | void
    onCancel?: () => void
  }
}

export type ModalEventData = {
  id?: number | string
  content?: React.ReactNode | ConfirmDescriptor
  options?: Record<string, unknown>
}

export type ModalEntry = {
  id: number | string
  content: React.ReactNode | ConfirmDescriptor | null
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
  showModal: (data: ModalEventData) => number | string
  hideModal: (id?: number | string) => void
  clearModals: () => void
} => {
  const snapshot = useSyncExternalStore(subscribe, getStack, getStack)

  return {
    stack: snapshot,
    showModal,
    hideModal,
    clearModals
  }
}

export const ModalProvider = ({
  children
}: {
  children: React.ReactNode
}): JSX.Element => (
  <>
    {children}
    <ModalManager />
  </>
)
