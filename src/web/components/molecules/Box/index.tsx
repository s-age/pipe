import { clsx } from 'clsx'
import type { JSX, ReactNode, ElementType } from 'react'

import { box } from './style.css'

type BoxProperties = {
  children?: ReactNode
  padding?: 's' | 'm' | 'l' | 'none'
  margin?: 's' | 'm' | 'l' | 'auto' | 'none'
  border?: boolean | 'thin' | 'thick'
  radius?: 's' | 'm' | 'l' | 'none'
  as?: ElementType
  className?: string
}

export const Box = ({
  children,
  padding = 'none',
  margin = 'none',
  border = false,
  radius = 'none',
  as: Component = 'div',
  className,
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
