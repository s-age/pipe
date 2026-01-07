import type { JSX } from 'react'
import { createPortal } from 'react-dom'

import { Box } from '@/components/molecules/Box'

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
  offsetCross?: number | null
  offsetMain?: number | null
}

const TooltipPortal = ({
  content,
  isVisible,
  placement,
  targetRect,
  offsetCross,
  offsetMain
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
    <Box ref={elementReference} className={className}>
      {content}
    </Box>,
    document.body
  )
}

export { TooltipPortal }
