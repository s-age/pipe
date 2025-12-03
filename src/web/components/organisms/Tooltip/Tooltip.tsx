import React from 'react'
import type { JSX } from 'react'

import { useTooltip } from './hooks/useTooltipHandlers'
import { tooltipContainer } from './style.css'

type TooltipProperties = {
  content: string
  children: React.ReactNode
  placement?: 'top' | 'bottom' | 'left' | 'right'
  className?: string
}

export const Tooltip: ({
  content,
  children,
  placement,
  className
}: TooltipProperties) => JSX.Element = ({
  content,
  children,
  placement,
  className = ''
}) => {
  const { onEnter, handleMouseLeave } = useTooltip(content, placement)

  return (
    <div
      className={`${tooltipContainer} ${className}`}
      onMouseEnter={onEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}
    </div>
  )
}
