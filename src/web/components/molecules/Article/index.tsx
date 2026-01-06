import { clsx } from 'clsx'
import type { JSX, ReactNode, HTMLAttributes } from 'react'

import { article, paddingS, paddingM, paddingL } from './style.css'

type ArticleProperties = {
  children?: ReactNode
  className?: string
  padding?: 's' | 'm' | 'l' | 'none'
} & Omit<HTMLAttributes<HTMLElement>, 'className'>

export const Article = ({
  children,
  className,
  padding = 'none',
  ...rest
}: ArticleProperties): JSX.Element => {
  const classNames = clsx(
    article,
    {
      [paddingS]: padding === 's',
      [paddingM]: padding === 'm',
      [paddingL]: padding === 'l'
    },
    className
  )

  return (
    <article className={classNames} {...rest}>
      {children}
    </article>
  )
}
