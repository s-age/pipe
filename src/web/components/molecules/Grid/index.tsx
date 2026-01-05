import { clsx } from 'clsx'
import type { JSX, ReactNode } from 'react'

import { grid } from './style.css'

type GridProperties = {
  children?: ReactNode
  columns?: '1' | '2' | '3' | '4' | 'auto-fit' | 'auto-fill'
  gap?: 's' | 'm' | 'l' | 'xl' | 'none'
  className?: string
}

export const Grid = ({
  children,
  columns = '1',
  gap = 'none',
  className,
  ...rest
}: GridProperties): JSX.Element => {
  const classNames = clsx(
    grid,
    {
      [`columns-${columns}`]: true,
      [`gap-${gap}`]: gap !== 'none'
    },
    className
  )

  return (
    <div className={classNames} {...rest}>
      {children}
    </div>
  )
}
