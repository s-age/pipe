import { LabelHTMLAttributes, JSX } from 'react'

import { labelStyle } from './style.css'

type LabelProps = {} & LabelHTMLAttributes<HTMLLabelElement>

const Label: (props: LabelProps) => JSX.Element = (props) => (
  <label className={labelStyle} {...props} />
)

export default Label
