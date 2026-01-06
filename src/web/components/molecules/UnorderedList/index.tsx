import { clsx } from 'clsx'
import type { JSX, ReactNode } from 'react'

import { unorderedList } from './style.css'

type UnorderedListProperties = {
  children?: ReactNode
  className?: string
  gap?: 's' | 'm' | 'l' | 'xl' | 'none'
  marker?: 'none' | 'disc' | 'circle' | 'square'
}

export const UnorderedList = ({
  children,
  className,
  gap = 'none',
  marker = 'none',
  ...rest
}: UnorderedListProperties): JSX.Element => {
  const classNames = clsx(
    unorderedList,
    {
      [`gap-${gap}`]: gap !== 'none',
      [`marker-${marker}`]: marker !== 'none'
    },
    className
  )

  return (
    <ul className={classNames} {...rest}>
      {children}
    </ul>
  )
}
