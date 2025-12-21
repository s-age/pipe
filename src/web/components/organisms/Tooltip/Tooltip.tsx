import { clsx } from 'clsx'
import React from 'react'
import type { JSX } from 'react'

import { useTooltipHandlers } from './hooks/useTooltipHandlers'
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
  const { onEnter, handleMouseLeave } = useTooltipHandlers(content, placement)

  return (
    <div
      className={clsx(tooltipContainer, className)}
      onMouseEnter={onEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}
    </div>
  )
}
