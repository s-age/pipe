import { clsx } from 'clsx'
import type { JSX, ReactNode, HTMLAttributes } from 'react'

import { footer, stickyBottom } from './style.css'

type FooterProperties = {
  children?: ReactNode
  className?: string
  sticky?: boolean
} & Omit<HTMLAttributes<HTMLElement>, 'className'>

export const Footer = ({
  children,
  className,
  sticky = false,
  ...rest
}: FooterProperties): JSX.Element => {
  const classNames = clsx(
    footer,
    {
      [stickyBottom]: sticky
    },
    className
  )

  return (
    <footer className={classNames} {...rest}>
      {children}
    </footer>
  )
}
