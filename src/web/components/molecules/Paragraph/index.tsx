import { clsx } from 'clsx'
import type { JSX, ReactNode, HTMLAttributes } from 'react'

import { paragraph } from './style.css'

type ParagraphProperties = {
  children?: ReactNode
  size?: 'xs' | 's' | 'm' | 'l' | 'xl'
  weight?: 'normal' | 'medium' | 'semibold' | 'bold'
  variant?: 'default' | 'muted' | 'error' | 'success'
  align?: 'left' | 'center' | 'right' | 'justify'
  className?: string
} & Omit<HTMLAttributes<HTMLParagraphElement>, 'className'>

export const Paragraph = ({
  children,
  size = 'm',
  weight = 'normal',
  variant = 'default',
  align = 'left',
  className,
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
