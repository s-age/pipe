import type { InputHTMLAttributes, JSX } from 'react'

import { checkboxStyle } from './style.css'

type CheckboxProperties = {} & InputHTMLAttributes<HTMLInputElement>

const Checkbox: (properties: CheckboxProperties) => JSX.Element = (properties) => (
  <input type="checkbox" className={checkboxStyle} {...properties} />
)

export default Checkbox
