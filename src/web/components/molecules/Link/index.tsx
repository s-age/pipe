import { clsx } from 'clsx'
import type { JSX, ReactNode, AnchorHTMLAttributes } from 'react'

import { link } from './style.css'

type LinkProperties = {
  href: string
  children?: ReactNode
  className?: string
  target?: '_blank' | '_self' | '_parent' | '_top'
  variant?: 'default' | 'subtle' | 'primary' | 'unstyled'
  'aria-label'?: string
  'aria-current'?:
    | 'page'
    | 'step'
    | 'location'
    | 'date'
    | 'time'
    | boolean
    | 'true'
    | 'false'
} & Omit<
  AnchorHTMLAttributes<HTMLAnchorElement>,
  'href' | 'target' | 'aria-label' | 'aria-current'
>

export const Link = ({
  children,
  className,
  href,
  target,
  variant,
  ...rest
}: LinkProperties): JSX.Element => {
  // Auto-apply unstyled variant when className is provided
  const finalVariant = variant ?? (className ? 'unstyled' : 'default')

  const classNames = clsx(
    link,
    {
      [`variant-${finalVariant}`]: true
    },
    className
  )

  return (
    <a
      href={href}
      target={target}
      rel={target === '_blank' ? 'noopener noreferrer' : undefined}
      className={classNames}
      {...rest}
    >
      {children}
    </a>
  )
}
