import { clsx } from 'clsx'
import type { JSX, ReactNode } from 'react'

import { emphasis } from './style.css'

type EmphasisProperties = {
  children?: ReactNode
  className?: string
}

export const Emphasis = ({
  children,
  className,
  ...rest
}: EmphasisProperties): JSX.Element => {
  const classNames = clsx(emphasis, className)

  return (
    <em className={classNames} {...rest}>
      {children}
    </em>
  )
}
