import { clsx } from 'clsx'
import type { JSX, ReactNode, HTMLAttributes } from 'react'

import { section, paddingS, paddingM, paddingL } from './style.css'

type SectionProperties = {
  children?: ReactNode
  className?: string
  padding?: 's' | 'm' | 'l' | 'none'
} & Omit<HTMLAttributes<HTMLElement>, 'className'>

export const Section = ({
  children,
  className,
  padding = 'none',
  ...rest
}: SectionProperties): JSX.Element => {
  const classNames = clsx(
    section,
    {
      [paddingS]: padding === 's',
      [paddingM]: padding === 'm',
      [paddingL]: padding === 'l'
    },
    className
  )

  return (
    <section className={classNames} {...rest}>
      {children}
    </section>
  )
}
