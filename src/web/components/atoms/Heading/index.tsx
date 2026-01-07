import clsx from 'clsx'
import type { HTMLAttributes, JSX } from 'react'

import { heading } from './style.css'

type HeadingProperties = {
  level?: 1 | 2 | 3 | 4 | 5 | 6
} & HTMLAttributes<HTMLHeadingElement>

export const Heading = ({
  children,
  className,
  level = 1,
  ...properties
}: HeadingProperties): JSX.Element => {
  const Tag = `h${level}` as const

  return (
    <Tag className={clsx(heading({ level }), className)} {...properties}>
      {children}
    </Tag>
  )
}

// Default export removed — use named export `Heading`
