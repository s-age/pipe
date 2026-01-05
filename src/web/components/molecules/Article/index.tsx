import { clsx } from 'clsx'
import type { JSX, ReactNode, HTMLAttributes } from 'react'

import { article, paddingS, paddingM, paddingL } from './style.css'

type ArticleProperties = {
  children?: ReactNode
  padding?: 's' | 'm' | 'l' | 'none'
  className?: string
} & Omit<HTMLAttributes<HTMLElement>, 'className'>

export const Article = ({
  children,
  padding = 'none',
  className,
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
