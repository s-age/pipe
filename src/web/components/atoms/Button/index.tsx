import clsx from 'clsx'
import type { ButtonHTMLAttributes, JSX } from 'react'

import { button } from './style.css'

type ButtonProperties = {
  hasBorder?: boolean
  kind?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'small' | 'default' | 'large' | 'xsmall'
  text?: 'bold' | 'uppercase'
  'aria-label'?: string
  'aria-expanded'?: boolean | 'true' | 'false'
} & ButtonHTMLAttributes<HTMLButtonElement>

export const Button = ({
  className,
  hasBorder = true,
  kind = 'primary',
  size = 'default',
  text,
  ...properties
}: ButtonProperties): JSX.Element => (
  <button
    className={clsx(button({ kind, size, text, hasBorder }), className)}
    {...properties}
  />
)

// Button is now a named export. Remove the default export to comply with
// the project's `import/no-default-export` rule.
