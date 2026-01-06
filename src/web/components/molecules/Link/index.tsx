import { clsx } from 'clsx'
import type { JSX, ReactNode, AnchorHTMLAttributes } from 'react'

import { link } from './style.css'

type LinkProperties = {
  href: string
  children?: ReactNode
  className?: string
  target?: '_blank' | '_self' | '_parent' | '_top'
  variant?: 'default' | 'subtle' | 'primary'
} & Omit<AnchorHTMLAttributes<HTMLAnchorElement>, 'href' | 'target'>

export const Link = ({
  children,
  className,
  href,
  target,
  variant = 'default',
  ...rest
}: LinkProperties): JSX.Element => {
  const classNames = clsx(
    link,
    {
      [`variant-${variant}`]: true
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
