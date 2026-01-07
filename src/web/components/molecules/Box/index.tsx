import { clsx } from 'clsx'
import type { JSX, ReactNode, ElementType, HTMLAttributes } from 'react'

import { box } from './style.css'

type BoxProperties = {
  as?: ElementType
  border?: boolean | 'thin' | 'thick'
  children?: ReactNode
  className?: string
  id?: string
  margin?: 's' | 'm' | 'l' | 'auto' | 'none'
  padding?: 's' | 'm' | 'l' | 'none'
  radius?: 's' | 'm' | 'l' | 'none'
} & Omit<HTMLAttributes<HTMLElement>, 'className'>

export const Box = ({
  as: Component = 'div',
  border = false,
  children,
  className,
  margin = 'none',
  padding = 'none',
  radius = 'none',
  ...rest
}: BoxProperties): JSX.Element => {
  const classNames = clsx(
    box,
    {
      [`padding-${padding}`]: padding !== 'none',
      [`margin-${margin}`]: margin !== 'none',
      [`border-${typeof border === 'string' ? border : 'default'}`]: border !== false,
      [`radius-${radius}`]: radius !== 'none'
    },
    className
  )

  return (
    <Component className={classNames} {...rest}>
      {children}
    </Component>
  )
}
