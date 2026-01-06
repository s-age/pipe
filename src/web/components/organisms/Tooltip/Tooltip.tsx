import { clsx } from 'clsx'
import React from 'react'
import type { JSX } from 'react'

import { useTooltipHandlers } from './hooks/useTooltipHandlers'
import { tooltipContainer } from './style.css'

type TooltipProperties = {
  children: React.ReactNode
  content: string
  className?: string
  placement?: 'top' | 'bottom' | 'left' | 'right'
}

export const Tooltip: ({
  children,
  content,
  className,
  placement
}: TooltipProperties) => JSX.Element = ({
  children,
  className = '',
  content,
  placement
}) => {
  const { handleMouseLeave, onEnter } = useTooltipHandlers(content, placement)

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
