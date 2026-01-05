import { clsx } from 'clsx'
import type { JSX, ReactNode } from 'react'

import { listItem } from './style.css'

type ListItemProperties = {
  children?: ReactNode
  padding?: 's' | 'm' | 'l' | 'none'
  className?: string
}

export const ListItem = ({
  children,
  padding = 'none',
  className,
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
