import { clsx } from 'clsx'
import type { JSX, ReactNode, ElementType, HTMLAttributes } from 'react'

import { flexColumn } from './style.css'

type FlexColumnProperties = {
  children?: ReactNode
  gap?: 's' | 'm' | 'l' | 'xl' | 'none'
  align?: 'start' | 'center' | 'end' | 'stretch'
  justify?: 'start' | 'center' | 'end' | 'between' | 'around'
  wrap?: boolean
  as?: ElementType
  className?: string
} & Omit<HTMLAttributes<HTMLElement>, 'className'>

export const FlexColumn = ({
  children,
  gap = 'none',
  align = 'stretch',
  justify = 'start',
  wrap = false,
  as: Element = 'div',
  className,
  ...rest
}: FlexColumnProperties): JSX.Element => {
  const classNames = clsx(
    flexColumn,
    {
      [`gap-${gap}`]: gap !== 'none',
      [`align-${align}`]: align !== 'stretch',
      [`justify-${justify}`]: justify !== 'start',
      wrap: wrap
    },
    className
  )

  return (
    <Element className={classNames} {...rest}>
      {children}
    </Element>
  )
}
