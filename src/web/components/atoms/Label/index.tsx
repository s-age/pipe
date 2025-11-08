import type { LabelHTMLAttributes, JSX } from 'react'

import { labelStyle } from './style.css'

type LabelProperties = {} & LabelHTMLAttributes<HTMLLabelElement>

const Label: (properties: LabelProperties) => JSX.Element = (properties) => (
  <label className={labelStyle} {...properties} />
)

export default Label
