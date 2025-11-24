import clsx from 'clsx'
import type { ButtonHTMLAttributes, JSX } from 'react'

import { button } from './style.css'

type ButtonProperties = {
  kind?: 'primary' | 'secondary' | 'ghost'
  size?: 'small' | 'default' | 'large' | 'xsmall'
  text?: 'bold' | 'uppercase'
  hasBorder?: boolean
} & ButtonHTMLAttributes<HTMLButtonElement>

export const Button = ({
  kind = 'primary',
  size = 'default',
  text,
  hasBorder = true,
  className,
  ...properties
}: ButtonProperties): JSX.Element => (
  <button
    className={clsx(button({ kind, size, text, hasBorder }), className)}
    {...properties}
  />
)

// Button is now a named export. Remove the default export to comply with
// the project's `import/no-default-export` rule.
