import { clsx } from 'clsx'
import type { JSX } from 'react'

import { text } from './style.css'

type TextProperties = {
  align?: 'left' | 'center' | 'right' | 'justify'
  children?: string
  className?: string
  size?: 'xs' | 's' | 'm' | 'l' | 'xl'
  truncate?: boolean
  variant?: 'default' | 'muted' | 'error' | 'success'
  weight?: 'normal' | 'medium' | 'semibold' | 'bold'
}

export const Text = ({
  align = 'left',
  children,
  className,
  size = 'm',
  truncate = false,
  variant = 'default',
  weight = 'normal',
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
