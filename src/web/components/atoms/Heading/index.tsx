import type { HTMLAttributes, JSX } from 'react'
import React from 'react'

import { h1Style } from './style.css'

type HeadingProperties = {
  level?: 1 | 2 | 3 | 4 | 5 | 6
} & HTMLAttributes<HTMLHeadingElement>

export const Heading: ({
  level,
  children,
  className,
  ...properties
}: HeadingProperties) => JSX.Element = ({
  level = 1,
  children,
  className,
  ...properties
}) => {
  const Tag = `h${level}`
  const headingClassName = `${level === 1 ? h1Style : ''} ${className || ''}`.trim()

  return React.createElement(
    Tag,
    { className: headingClassName, ...properties },
    children
  )
}

// Default export removed — use named export `Heading`
