import React, { useState, JSX } from 'react'

import { tooltipContainer, tooltipText } from './style.css'

type TooltipProps = {
  content: string
  children: React.ReactNode
}

const Tooltip: ({ content, children }: TooltipProps) => JSX.Element = ({
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
