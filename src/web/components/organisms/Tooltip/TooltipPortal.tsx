import type { JSX } from 'react'
import { createPortal } from 'react-dom'

import { useTooltipLifecycle } from './hooks/useTooltipLifecycle'
import {
  tooltipText,
  placementTop,
  placementBottom,
  placementLeft,
  placementRight,
  visible
} from './style.css'

type Properties = {
  content: React.ReactNode
  isVisible: boolean
  placement: 'top' | 'bottom' | 'left' | 'right'
  targetRect: DOMRect | null
  offsetMain?: number | null
  offsetCross?: number | null
}

const TooltipPortal = ({
  content,
  isVisible,
  placement,
  targetRect,
  offsetMain,
  offsetCross
}: Properties): JSX.Element | null => {
  const elementReference = useTooltipLifecycle({
    isVisible,
    placement,
    targetRect,
    offsetMain,
    offsetCross
  })

  const className = `${tooltipText} ${
    placement === 'top'
      ? placementTop
      : placement === 'bottom'
        ? placementBottom
        : placement === 'left'
          ? placementLeft
          : placementRight
  } ${isVisible ? visible : ''}`

  if (typeof document === 'undefined') return null

  return createPortal(
    <div ref={elementReference} className={className}>
      {content}
    </div>,
    document.body
  )
}

export { TooltipPortal }
