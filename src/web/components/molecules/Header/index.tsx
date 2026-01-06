import { clsx } from 'clsx'
import type { JSX, ReactNode, HTMLAttributes } from 'react'

import { header, stickyTop } from './style.css'

type HeaderProperties = {
  children?: ReactNode
  className?: string
  sticky?: boolean
} & Omit<HTMLAttributes<HTMLElement>, 'className'>

export const Header = ({
  children,
  className,
  sticky = false,
  ...rest
}: HeaderProperties): JSX.Element => {
  const classNames = clsx(
    header,
    {
      [stickyTop]: sticky
    },
    className
  )

  return (
    <header className={classNames} {...rest}>
      {children}
    </header>
  )
}
