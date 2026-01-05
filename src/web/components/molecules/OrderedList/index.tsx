import { clsx } from 'clsx'
import type { JSX, ReactNode } from 'react'

import { orderedList } from './style.css'

type OrderedListProperties = {
  children?: ReactNode
  gap?: 's' | 'm' | 'l' | 'xl' | 'none'
  type?: '1' | 'a' | 'A' | 'i' | 'I'
  className?: string
}

export const OrderedList = ({
  children,
  gap = 'none',
  type = '1',
  className,
  ...rest
}: OrderedListProperties): JSX.Element => {
  const classNames = clsx(
    orderedList,
    {
      [`gap-${gap}`]: gap !== 'none'
    },
    className
  )

  return (
    <ol className={classNames} type={type} {...rest}>
      {children}
    </ol>
  )
}
