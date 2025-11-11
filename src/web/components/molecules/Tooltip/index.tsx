import type { JSX } from 'react'
import React from 'react'

import { useTooltip } from './hooks/useTooltipHandlers'
import { tooltipContainer, tooltipText } from './style.css'

type TooltipProperties = {
  content: string
  children: React.ReactNode
}

export const Tooltip: ({ content, children }: TooltipProperties) => JSX.Element = ({
  content,
  children
}) => {
  const { isVisible, handleMouseEnter, handleMouseLeave } = useTooltip()

  return (
    <div
      className={tooltipContainer}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}
      {isVisible && <div className={tooltipText}>{content}</div>}
    </div>
  )
}

// (Removed temporary default export) Use named export `Tooltip`.
