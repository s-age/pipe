import { clsx } from 'clsx'
import React from 'react'
import type { JSX } from 'react'

import { Box } from '@/components/molecules/Box'

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
  const { handleMouseLeave, onEnter, onFocus, onBlur, tooltipId } = useTooltipHandlers(
    content,
    placement
  )

  return (
    <Box
      className={clsx(tooltipContainer, className)}
      onMouseEnter={onEnter}
      onMouseLeave={handleMouseLeave}
      onFocus={onFocus}
      onBlur={onBlur}
      aria-describedby={tooltipId}
    >
      {children}
    </Box>
  )
}
