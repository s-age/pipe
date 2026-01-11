import { clsx } from 'clsx'
import type { JSX, ReactNode } from 'react'

import { heightVariants, scrollArea } from './style.css'

type ScrollAreaProperties = {
  children?: ReactNode
  className?: string
  direction?: 'vertical' | 'horizontal' | 'both'
  height?: keyof typeof heightVariants
}

export const ScrollArea = ({
  children,
  className,
  direction = 'vertical',
  height,
  ...rest
}: ScrollAreaProperties): JSX.Element => {
  const classNames = clsx(
    scrollArea,
    {
      [`direction-${direction}`]: true
    },
    height && heightVariants[height],
    className
  )

  return (
    <div className={classNames} {...rest}>
      {children}
    </div>
  )
}
