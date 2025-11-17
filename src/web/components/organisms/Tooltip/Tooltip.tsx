import type { JSX } from 'react'
import { useCallback } from 'react'

import { useTooltip } from './hooks/useTooltipHandlers'
import { tooltipContainer } from './style.css'

type TooltipProperties = {
  content: string
  children: React.ReactNode
}

export const Tooltip: ({ content, children }: TooltipProperties) => JSX.Element = ({
  content,
  children
}) => {
  const { handleMouseEnter, handleMouseLeave } = useTooltip()

  const onEnter = useCallback(
    (event: React.MouseEvent<HTMLElement>) => handleMouseEnter(event, { content }),
    [handleMouseEnter, content]
  )

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

// (Removed temporary default export) Use named export `Tooltip`.
