import { clsx } from 'clsx'
import type { JSX } from 'react'

import { text } from './style.css'

type TextProperties = {
  children?: string
  size?: 'xs' | 's' | 'm' | 'l' | 'xl'
  weight?: 'normal' | 'medium' | 'semibold' | 'bold'
  variant?: 'default' | 'muted' | 'error' | 'success'
  align?: 'left' | 'center' | 'right' | 'justify'
  truncate?: boolean
  className?: string
}

export const Text = ({
  children,
  size = 'm',
  weight = 'normal',
  variant = 'default',
  align = 'left',
  truncate = false,
  className,
  ...rest
}: TextProperties): JSX.Element => {
  const classNames = clsx(
    text,
    {
      [`size-${size}`]: true,
      [`weight-${weight}`]: weight !== 'normal',
      [`variant-${variant}`]: variant !== 'default',
      [`align-${align}`]: align !== 'left',
      truncate: truncate
    },
    className
  )

  return (
    <span className={classNames} {...rest}>
      {children}
    </span>
  )
}
