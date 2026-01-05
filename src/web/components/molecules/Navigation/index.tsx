import { clsx } from 'clsx'
import type { JSX, ReactNode, HTMLAttributes } from 'react'

import { navigation } from './style.css'

type NavigationProperties = {
  children?: ReactNode
  ariaLabel?: string
  className?: string
} & Omit<HTMLAttributes<HTMLElement>, 'className' | 'aria-label'>

export const Navigation = ({
  children,
  ariaLabel,
  className,
  ...rest
}: NavigationProperties): JSX.Element => {
  return (
    <nav className={clsx(navigation, className)} aria-label={ariaLabel} {...rest}>
      {children}
    </nav>
  )
}
