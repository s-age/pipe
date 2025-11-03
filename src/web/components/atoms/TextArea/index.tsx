import { TextareaHTMLAttributes, JSX } from 'react'

import { textareaStyle } from './style.css'

type TextAreaProps = {} & TextareaHTMLAttributes<HTMLTextAreaElement>

const TextArea: (props: TextAreaProps) => JSX.Element = (props) => (
  <textarea className={textareaStyle} {...props} />
)

export default TextArea
