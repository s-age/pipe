import { clsx } from 'clsx'
import { forwardRef } from 'react'
import type { JSX, ReactNode, HTMLAttributes } from 'react'

import { listItem } from './style.css'

type ListItemProperties = {
  children?: ReactNode
  className?: string
  padding?: 's' | 'm' | 'l' | 'none'
} & Omit<HTMLAttributes<HTMLLIElement>, 'className'>

export const ListItem = forwardRef<HTMLLIElement, ListItemProperties>(
  ({ children, className, padding = 'none', ...rest }, reference): JSX.Element => {
    const classNames = clsx(
      listItem,
      {
        [`padding-${padding}`]: padding !== 'none'
      },
      className
    )

    return (
      <li className={classNames} ref={reference} {...rest}>
        {children}
      </li>
    )
  }
)

ListItem.displayName = 'ListItem'
