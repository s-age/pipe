import { clsx } from 'clsx'
import type { JSX, ReactNode, HTMLAttributes } from 'react'

import { footer, stickyBottom } from './style.css'

type FooterProperties = {
  children?: ReactNode
  sticky?: boolean
  stickyOffset?: number
  className?: string
} & Omit<HTMLAttributes<HTMLElement>, 'className'>

export const Footer = ({
  children,
  sticky = false,
  stickyOffset = 0,
  className,
  ...rest
}: FooterProperties): JSX.Element => {
  const classNames = clsx(
    footer,
    {
      [stickyBottom]: sticky
    },
    className
  )

  const style = sticky ? { bottom: stickyOffset } : undefined

  return (
    <footer className={classNames} style={style} {...rest}>
      {children}
    </footer>
  )
}
