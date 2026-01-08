import { clsx } from 'clsx'
import React from 'react'
import type { ReactNode, HTMLAttributes } from 'react'

import { unorderedList } from './style.css'

type UnorderedListProperties = {
  children?: ReactNode
  className?: string
  gap?: 's' | 'm' | 'l' | 'xl' | 'none'
  marker?: 'none' | 'disc' | 'circle' | 'square'
} & Omit<HTMLAttributes<HTMLUListElement>, 'className'>

export const UnorderedList = React.forwardRef<
  HTMLUListElement,
  UnorderedListProperties
>(({ children, className, gap = 'none', marker = 'none', ...rest }, reference) => {
  const classNames = clsx(
    unorderedList,
    {
      [`gap-${gap}`]: gap !== 'none',
      [`marker-${marker}`]: marker !== 'none'
    },
    className
  )

  return (
    <ul ref={reference} className={classNames} {...rest}>
      {children}
    </ul>
  )
})

UnorderedList.displayName = 'UnorderedList'
