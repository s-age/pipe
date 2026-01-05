import { clsx } from 'clsx'
import type { JSX, ReactNode } from 'react'

import { unorderedList } from './style.css'

type UnorderedListProperties = {
  children?: ReactNode
  gap?: 's' | 'm' | 'l' | 'xl' | 'none'
  marker?: 'none' | 'disc' | 'circle' | 'square'
  className?: string
}

export const UnorderedList = ({
  children,
  gap = 'none',
  marker = 'none',
  className,
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
