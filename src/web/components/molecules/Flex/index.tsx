import { clsx } from 'clsx'
import type { JSX, ReactNode, ElementType, HTMLAttributes } from 'react'

import { flex } from './style.css'

type FlexProperties = {
  align?: 'start' | 'center' | 'end' | 'baseline' | 'stretch'
  as?: ElementType
  children?: ReactNode
  className?: string
  gap?: 's' | 'm' | 'l' | 'xl' | 'none'
  justify?: 'start' | 'center' | 'end' | 'between' | 'around'
  wrap?: boolean
} & Omit<HTMLAttributes<HTMLElement>, 'className'>

export const Flex = ({
  align = 'stretch',
  as: Element = 'div',
  children,
  className,
  gap = 'none',
  justify = 'start',
  wrap = false,
  ...rest
}: FlexProperties): JSX.Element => {
  const classNames = clsx(
    flex,
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
