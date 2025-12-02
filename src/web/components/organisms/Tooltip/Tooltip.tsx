import React from 'react'
import type { JSX } from 'react'

import { useTooltip } from './hooks/useTooltipHandlers'
import { tooltipContainer } from './style.css'

type TooltipProperties = {
  content: string
  children: React.ReactNode
  placement?: 'top' | 'bottom' | 'left' | 'right'
}

export const Tooltip: ({
  content,
  children,
  placement
}: TooltipProperties) => JSX.Element = ({ content, children, placement }) => {
  const { onEnter, handleMouseLeave } = useTooltip(content, placement)

  return (
    <div
      className={tooltipContainer}
      onMouseEnter={onEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}
    </div>
  )
}
