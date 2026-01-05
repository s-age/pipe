import { clsx } from 'clsx'
import type { JSX, ReactNode, AnchorHTMLAttributes } from 'react'

import { link } from './style.css'

type LinkProperties = {
  children?: ReactNode
  href: string
  target?: '_blank' | '_self' | '_parent' | '_top'
  variant?: 'default' | 'subtle' | 'primary'
  className?: string
} & Omit<AnchorHTMLAttributes<HTMLAnchorElement>, 'href' | 'target'>

export const Link = ({
  children,
  href,
  target,
  variant = 'default',
  className,
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
