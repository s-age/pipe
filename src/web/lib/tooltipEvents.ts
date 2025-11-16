import { eventBus } from './eventBus'

export type TooltipEventData = {
  id?: number | string
  rect?: DOMRect
  placement?: 'top' | 'bottom' | 'left' | 'right'
  content?: React.ReactNode
  // offset along the main axis (distance from target) in px
  offsetMain?: number
  // offset along the cross axis (shift perpendicular to main axis) in px
  offsetCross?: number
}

const TOOLTIP_SHOW = 'tooltip:show'
const TOOLTIP_HIDE = 'tooltip:hide'
const TOOLTIP_CLEAR = 'tooltip:clear'

export const emitTooltip = {
  show: (data: TooltipEventData): void => {
    eventBus.emit(TOOLTIP_SHOW, data)
  },
  hide: (id?: number | string): void => {
    eventBus.emit(TOOLTIP_HIDE, { id })
  },
  clear: (): void => {
    eventBus.emit(TOOLTIP_CLEAR, {})
  }
}

export const onTooltipShow = (
  callback: (data: TooltipEventData) => void
): (() => void) => eventBus.on(TOOLTIP_SHOW, callback)

export const onTooltipHide = (
  callback: (data: { id?: number | string }) => void
): (() => void) => eventBus.on(TOOLTIP_HIDE, callback)

export const onTooltipClear = (callback: () => void): (() => void) =>
  eventBus.on(TOOLTIP_CLEAR, callback)

// Global listeners: clear all tooltips on window blur or pointerdown outside
if (typeof window !== 'undefined' && typeof document !== 'undefined') {
  // Clear on window blur (user switches tabs / apps)
  window.addEventListener('blur', () => emitTooltip.clear())

  // Clear on any pointerdown (click/tap) to hide tooltips when user interacts
  document.addEventListener('pointerdown', () => emitTooltip.clear())
}
