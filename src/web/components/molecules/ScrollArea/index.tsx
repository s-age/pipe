import { clsx } from 'clsx'
import type { JSX, ReactNode } from 'react'

import { scrollArea } from './style.css'

type ScrollAreaProperties = {
  children?: ReactNode
  direction?: 'vertical' | 'horizontal' | 'both'
  className?: string
}

export const ScrollArea = ({
  children,
  direction = 'vertical',
  className,
  ...rest
}: ScrollAreaProperties): JSX.Element => {
  const classNames = clsx(
    scrollArea,
    {
      [`direction-${direction}`]: true
    },
    className
  )

  return (
    <div className={classNames} {...rest}>
      {children}
    </div>
  )
}
