import { clsx } from 'clsx'
import type { JSX, ReactNode, HTMLAttributes } from 'react'

import { header, stickyTop } from './style.css'

type HeaderProperties = {
  children?: ReactNode
  sticky?: boolean
  stickyOffset?: number
  className?: string
} & Omit<HTMLAttributes<HTMLElement>, 'className'>

export const Header = ({
  children,
  sticky = false,
  stickyOffset = 0,
  className,
  ...rest
}: HeaderProperties): JSX.Element => {
  const classNames = clsx(
    header,
    {
      [stickyTop]: sticky
    },
    className
  )

  const style = sticky ? { top: stickyOffset } : undefined

  return (
    <header className={classNames} style={style} {...rest}>
      {children}
    </header>
  )
}
