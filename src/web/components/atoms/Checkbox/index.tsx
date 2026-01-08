import clsx from 'clsx'
import { forwardRef } from 'react'
import type { InputHTMLAttributes, JSX } from 'react'

import { checkboxStyle } from './style.css'

type CheckboxProperties = {
  /**
   * Provides an accessible label for the checkbox when a visible label is not present.
   * Use this for checkboxes without associated <label> elements.
   */
  'aria-label'?: string
  /**
   * Links the checkbox to descriptive text such as error messages or help text.
   * Provide the ID(s) of the describing element(s).
   */
  'aria-describedby'?: string
} & InputHTMLAttributes<HTMLInputElement>

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
