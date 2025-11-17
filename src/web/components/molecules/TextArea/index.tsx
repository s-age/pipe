import type { TextareaHTMLAttributes, JSX } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn
} from 'react-hook-form'

import { useTextArea } from './hooks/useTextArea'
import { textareaStyle } from './style.css'

type TextAreaProperties = Omit<
  TextareaHTMLAttributes<HTMLTextAreaElement>,
  'onChange'
> & {
  onChange?: (value: string) => void
  register?: UseFormRegister<FieldValues>
  name?: string
}

export const TextArea: (properties: TextAreaProperties) => JSX.Element = (
  properties
) => {
  const {
    onChange: _onChange,
    name,
    register: _register,
    ...restProperties
  } = properties
  // reference the binding to satisfy lint rules (we intentionally don't spread it)
  void _register
  // intentionally reference `_onChange` so linters know it's excluded from
  // `restProps` which will be spread onto the native textarea. The component's
  // onChange has a different signature (value:string) and we bridge it via the hook.
  void _onChange

  const { id, registerProperties, visibleValue, handleChange } = useTextArea(
    properties as unknown as Parameters<typeof useTextArea>[0]
  )

  const rp = registerProperties as UseFormRegisterReturn | undefined

  return (
    <textarea
      id={id}
      className={textareaStyle}
      {...restProperties}
      {...(visibleValue !== undefined ? { value: visibleValue } : {})}
      name={name}
      {...(rp ? (rp as unknown as Record<string, unknown>) : {})}
      onChange={handleChange}
    />
  )
}

// (Removed temporary default export) Use named export `TextArea`.
