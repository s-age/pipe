import type { TextareaHTMLAttributes, JSX } from 'react'

import { textareaStyle } from './style.css'

type TextAreaProperties = {} & TextareaHTMLAttributes<HTMLTextAreaElement>

const TextArea: (properties: TextAreaProperties) => JSX.Element = (properties) => (
  <textarea className={textareaStyle} {...properties} />
)

export default TextArea
