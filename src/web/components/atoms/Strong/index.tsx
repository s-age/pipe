import { clsx } from 'clsx'
import type { JSX, ReactNode } from 'react'

import { strong } from './style.css'

type StrongProperties = {
  children?: ReactNode
  className?: string
}

export const Strong = ({
  children,
  className,
  ...rest
}: StrongProperties): JSX.Element => {
  const classNames = clsx(strong, className)

  return (
    <strong className={classNames} {...rest}>
      {children}
    </strong>
  )
}
