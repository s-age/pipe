import type { LabelHTMLAttributes, JSX } from 'react'

import { labelStyle } from './style.css'

type LabelProperties = {} & LabelHTMLAttributes<HTMLLabelElement>

export const Label: (properties: LabelProperties) => JSX.Element = (properties) => (
  <label className={labelStyle} {...properties} />
)

// Default export removed — use named export `Label`
