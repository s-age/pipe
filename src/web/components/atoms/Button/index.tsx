import clsx from 'clsx'
import { ButtonHTMLAttributes, JSX } from 'react'

import { button } from './style.css'

type ButtonProps = {
  kind?: 'primary' | 'secondary' | 'ghost'
  size?: 'small' | 'default' | 'large' | 'xsmall'
  text?: 'bold' | 'uppercase'
  hasBorder?: boolean
} & ButtonHTMLAttributes<HTMLButtonElement>

const Button: (props: ButtonProps) => JSX.Element = ({
  kind = 'primary',
  size = 'default',
  text,
  hasBorder = true,
  className,
  ...props
}) => (
  <button
    className={clsx(button({ kind, size, text, hasBorder }), className)}
    {...props}
  />
)

export default Button
