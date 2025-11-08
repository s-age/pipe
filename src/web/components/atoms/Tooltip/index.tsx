import type { JSX } from 'react'
import React, { useState } from 'react'

import { tooltipContainer, tooltipText } from './style.css'

type TooltipProperties = {
  content: string
  children: React.ReactNode
}

const Tooltip: ({ content, children }: TooltipProperties) => JSX.Element = ({
  content,
  children,
}) => {
  const [isVisible, setIsVisible] = useState(false)

  return (
    <div
      className={tooltipContainer}
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && <div className={tooltipText}>{content}</div>}
    </div>
  )
}

export default Tooltip
