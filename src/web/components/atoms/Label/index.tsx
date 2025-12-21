import clsx from 'clsx'
import type { LabelHTMLAttributes, JSX } from 'react'

import { labelStyle } from './style.css'

type LabelProperties = {
  required?: boolean
} & LabelHTMLAttributes<HTMLLabelElement>

export const Label = ({
  required,
  children,
  className,
  ...properties
}: LabelProperties): JSX.Element => (
  <label className={clsx(labelStyle, className)} {...properties}>
    {children}
    {required && <span aria-label="required"> *</span>}
  </label>
)
