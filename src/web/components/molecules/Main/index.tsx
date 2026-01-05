import { clsx } from 'clsx'
import type { JSX, ReactNode, HTMLAttributes } from 'react'

import { main } from './style.css'

type MainProperties = {
  children?: ReactNode
  className?: string
} & Omit<HTMLAttributes<HTMLElement>, 'className'>

export const Main = ({
  children,
  className,
  ...rest
}: MainProperties): JSX.Element => {
  return (
    <main className={clsx(main, className)} {...rest}>
      {children}
    </main>
  )
}
