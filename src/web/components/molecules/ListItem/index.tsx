import { clsx } from 'clsx'
import type { JSX, ReactNode } from 'react'

import { listItem } from './style.css'

type ListItemProperties = {
  children?: ReactNode
  className?: string
  padding?: 's' | 'm' | 'l' | 'none'
}

export const ListItem = ({
  children,
  className,
  padding = 'none',
  ...rest
}: ListItemProperties): JSX.Element => {
  const classNames = clsx(
    listItem,
    {
      [`padding-${padding}`]: padding !== 'none'
    },
    className
  )

  return (
    <li className={classNames} {...rest}>
      {children}
    </li>
  )
}
