import { clsx } from 'clsx'
import type { JSX, ReactNode, HTMLAttributes } from 'react'

import { paragraph } from './style.css'

type ParagraphProperties = {
  align?: 'left' | 'center' | 'right' | 'justify'
  children?: ReactNode
  className?: string
  size?: 'xs' | 's' | 'm' | 'l' | 'xl' | 'unstyled'
  variant?: 'default' | 'muted' | 'error' | 'success' | 'unstyled'
  weight?: 'normal' | 'medium' | 'semibold' | 'bold'
} & Omit<HTMLAttributes<HTMLParagraphElement>, 'className'>

export const Paragraph = ({
  align = 'left',
  children,
  className,
  size,
  variant,
  weight = 'normal',
  ...rest
}: ParagraphProperties): JSX.Element => {
  // Auto-apply unstyled variant and size when className is provided
  const finalVariant = variant ?? (className ? 'unstyled' : 'default')
  const finalSize = size ?? (className ? 'unstyled' : 'm')

  const classNames = clsx(
    paragraph,
    {
      [`size-${finalSize}`]: true,
      [`weight-${weight}`]: weight !== 'normal',
      [`variant-${finalVariant}`]: finalVariant !== 'default',
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
