import { InputHTMLAttributes, JSX } from 'react'

import { inputStyle } from './style.css'

type InputTextProps = {} & InputHTMLAttributes<HTMLInputElement>

const InputText: (props: InputTextProps) => JSX.Element = (props) => (
  <input type="text" className={inputStyle} {...props} />
)

export default InputText
