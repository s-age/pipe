import type { InputHTMLAttributes, JSX } from 'react'

import { checkboxStyle } from './style.css'

type CheckboxProperties = {} & InputHTMLAttributes<HTMLInputElement>

export const Checkbox: (properties: CheckboxProperties) => JSX.Element = (
  properties
) => <input type="checkbox" className={checkboxStyle} {...properties} />

// Default export removed — use named export `Checkbox`
