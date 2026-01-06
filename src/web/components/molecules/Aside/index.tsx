import { clsx } from 'clsx'
import type { JSX, ReactNode, HTMLAttributes } from 'react'

import { aside, positionLeft, positionRight } from './style.css'

type AsideProperties = {
  children?: ReactNode
  className?: string
  position?: 'left' | 'right'
} & Omit<HTMLAttributes<HTMLElement>, 'className'>

export const Aside = ({
  children,
  className,
  position,
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
