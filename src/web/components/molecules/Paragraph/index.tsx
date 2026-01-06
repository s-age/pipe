import { clsx } from 'clsx'
import type { JSX, ReactNode, HTMLAttributes } from 'react'

import { paragraph } from './style.css'

type ParagraphProperties = {
  align?: 'left' | 'center' | 'right' | 'justify'
  children?: ReactNode
  className?: string
  size?: 'xs' | 's' | 'm' | 'l' | 'xl'
  variant?: 'default' | 'muted' | 'error' | 'success'
  weight?: 'normal' | 'medium' | 'semibold' | 'bold'
} & Omit<HTMLAttributes<HTMLParagraphElement>, 'className'>

export const Paragraph = ({
  align = 'left',
  children,
  className,
  size = 'm',
  variant = 'default',
  weight = 'normal',
  ...rest
}: ParagraphProperties): JSX.Element => {
  const classNames = clsx(
    paragraph,
    {
      [`size-${size}`]: true,
      [`weight-${weight}`]: weight !== 'normal',
      [`variant-${variant}`]: variant !== 'default',
      [`align-${align}`]: align !== 'left'
    },
    className
  )

  return (
    <p className={classNames} {...rest}>
      {children}
    </p>
  )
}
