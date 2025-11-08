import type { InputHTMLAttributes, JSX } from 'react'

import { inputStyle } from './style.css'

type InputTextProperties = {} & InputHTMLAttributes<HTMLInputElement>

const InputText: (properties: InputTextProperties) => JSX.Element = (properties) => (
  <input type="text" className={inputStyle} {...properties} />
)

export default InputText
