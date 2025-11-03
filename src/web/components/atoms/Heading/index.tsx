import React, { HTMLAttributes, JSX } from 'react'

import { h1Style } from './style.css'

type HeadingProps = {
  level?: 1 | 2 | 3 | 4 | 5 | 6
} & HTMLAttributes<HTMLHeadingElement>

const Heading: ({
  level,
  children,
  className,
  ...props
}: HeadingProps) => JSX.Element = ({ level = 1, children, className, ...props }) => {
  const Tag = `h${level}`
  const headingClassName = `${level === 1 ? h1Style : ''} ${className || ''}`.trim()

  return React.createElement(Tag, { className: headingClassName, ...props }, children)
}

export default Heading
