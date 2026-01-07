import { clsx } from 'clsx'
import type { JSX, ReactNode } from 'react'

import { scrollArea } from './style.css'

type ScrollAreaProperties = {
  children?: ReactNode
  className?: string
  direction?: 'vertical' | 'horizontal' | 'both'
}

export const ScrollArea = ({
  children,
  className,
  direction = 'vertical',
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
