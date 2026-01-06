import { clsx } from 'clsx'
import type { JSX, ReactNode } from 'react'

import { orderedList } from './style.css'

type OrderedListProperties = {
  children?: ReactNode
  className?: string
  gap?: 's' | 'm' | 'l' | 'xl' | 'none'
  type?: '1' | 'a' | 'A' | 'i' | 'I'
}

export const OrderedList = ({
  children,
  className,
  gap = 'none',
  type = '1',
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
