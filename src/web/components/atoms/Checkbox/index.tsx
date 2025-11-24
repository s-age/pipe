import clsx from 'clsx'
import { forwardRef } from 'react'
import type { InputHTMLAttributes, JSX } from 'react'

import { checkboxStyle } from './style.css'

type CheckboxProperties = {} & InputHTMLAttributes<HTMLInputElement>

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProperties>(
  ({ className, ...properties }, reference): JSX.Element => (
    <input
      ref={reference}
      type="checkbox"
      className={clsx(checkboxStyle, className)}
      {...properties}
    />
  )
)

Checkbox.displayName = 'Checkbox'
