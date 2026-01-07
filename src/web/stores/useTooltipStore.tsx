import { useSyncExternalStore } from 'react'

export type TooltipEventData = {
  content?: React.ReactNode
  id?: number | string
  offsetCross?: number
  offsetMain?: number
  placement?: 'top' | 'bottom' | 'left' | 'right'
  rect?: DOMRect | null
}

export type ActiveTooltip = TooltipEventData | null

const listeners: Set<() => void> = new Set()
let active: ActiveTooltip = null
let autoHideTimer: ReturnType<typeof setTimeout> | null = null

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
  // Clear any existing auto-hide timer and start a new one for 5s.
  if (autoHideTimer) {
    clearTimeout(autoHideTimer)
    autoHideTimer = null
  }
  autoHideTimer = setTimeout(() => {
    // Only clear if the active tooltip is the same id we showed (or clear generally)
    if (!active) return
    if (data.id == null || String(active.id) === String(data.id)) {
      active = null
      notify()
    }
    autoHideTimer = null
  }, 5000)
  notify()
}

export const hideTooltip = (id?: number | string): void => {
  // If hiding manually, clear any pending auto-hide timer.
  if (autoHideTimer) {
    clearTimeout(autoHideTimer)
    autoHideTimer = null
  }
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
  if (autoHideTimer) {
    clearTimeout(autoHideTimer)
    autoHideTimer = null
  }
  notify()
}

export const useTooltipStore = (): {
  active: ActiveTooltip
  clearTooltips: () => void
  hideTooltip: (id?: number | string) => void
  showTooltip: (data: TooltipEventData) => void
} => {
  const snapshot = useSyncExternalStore(subscribe, getActive, getActive)

  return {
    active: snapshot,
    showTooltip,
    hideTooltip,
    clearTooltips
  }
}
