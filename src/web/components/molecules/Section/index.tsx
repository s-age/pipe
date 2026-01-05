import { clsx } from 'clsx'
import type { JSX, ReactNode, HTMLAttributes } from 'react'

import { section, paddingS, paddingM, paddingL } from './style.css'

type SectionProperties = {
  children?: ReactNode
  padding?: 's' | 'm' | 'l' | 'none'
  className?: string
} & Omit<HTMLAttributes<HTMLElement>, 'className'>

export const Section = ({
  children,
  padding = 'none',
  className,
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
