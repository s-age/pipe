import { clsx } from 'clsx'
import type { JSX, ReactNode, HTMLAttributes } from 'react'

import { aside, positionLeft, positionRight } from './style.css'

type AsideProperties = {
  children?: ReactNode
  position?: 'left' | 'right'
  className?: string
} & Omit<HTMLAttributes<HTMLElement>, 'className'>

export const Aside = ({
  children,
  position,
  className,
  ...rest
}: AsideProperties): JSX.Element => {
  const classNames = clsx(
    aside,
    {
      [positionLeft]: position === 'left',
      [positionRight]: position === 'right'
    },
    className
  )

  return (
    <aside className={classNames} {...rest}>
      {children}
    </aside>
  )
}
