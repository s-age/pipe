import clsx from 'clsx'
import type { ButtonHTMLAttributes, JSX } from 'react'

import { button } from './style.css'

type ButtonProperties = {
  kind?: 'primary' | 'secondary' | 'ghost'
  size?: 'small' | 'default' | 'large' | 'xsmall'
  text?: 'bold' | 'uppercase'
  hasBorder?: boolean
} & ButtonHTMLAttributes<HTMLButtonElement>

const Button: (properties: ButtonProperties) => JSX.Element = ({
  kind = 'primary',
  size = 'default',
  text,
  hasBorder = true,
  className,
  ...properties
}) => (
  <button
    className={clsx(button({ kind, size, text, hasBorder }), className)}
    {...properties}
  />
)

export default Button
