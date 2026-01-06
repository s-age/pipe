import { clsx } from 'clsx'
import type { JSX, ReactNode, HTMLAttributes } from 'react'

import { navigation } from './style.css'

type NavigationProperties = {
  ariaLabel?: string
  children?: ReactNode
  className?: string
} & Omit<HTMLAttributes<HTMLElement>, 'className' | 'aria-label'>

export const Navigation = ({
  ariaLabel,
  children,
  className,
  ...rest
}: NavigationProperties): JSX.Element => (
  <nav className={clsx(navigation, className)} aria-label={ariaLabel} {...rest}>
    {children}
  </nav>
)
