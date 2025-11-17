import { useSyncExternalStore } from 'react'

export type TooltipEventData = {
  id?: number | string
  rect?: DOMRect | null
  placement?: 'top' | 'bottom' | 'left' | 'right'
  content?: React.ReactNode
  offsetMain?: number
  offsetCross?: number
}

export type ActiveTooltip = TooltipEventData | null

const listeners: Set<() => void> = new Set()
let active: ActiveTooltip = null

export const getActive = (): ActiveTooltip => active

export const subscribe = (callback: () => void): (() => void) => {
  listeners.add(callback)

  return () => listeners.delete(callback)
}

const notify = (): void => listeners.forEach((l) => l())

export const showTooltip = (data: TooltipEventData): void => {
  active = {
    ...data
  }
  notify()
}

export const hideTooltip = (id?: number | string): void => {
  if (!id) {
    active = null
    notify()

    return
  }

  if (!active) return
  if (String(active.id) === String(id)) {
    active = null
    notify()
  }
}

export const clearTooltips = (): void => {
  active = null
  notify()
}

export const useTooltipStore = (): {
  active: ActiveTooltip
  showTooltip: (data: TooltipEventData) => void
  hideTooltip: (id?: number | string) => void
  clearTooltips: () => void
} => {
  const snapshot = useSyncExternalStore(subscribe, getActive, getActive)

  return {
    active: snapshot,
    showTooltip,
    hideTooltip,
    clearTooltips
  }
}
