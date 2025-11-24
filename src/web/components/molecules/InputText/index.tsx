import type { InputHTMLAttributes, JSX } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn
} from 'react-hook-form'

import { useInputText } from './hooks/useInputText'
import { inputStyle } from './style.css'

type InputTextProperties = {
  register?: UseFormRegister<FieldValues>
  name?: string
} & InputHTMLAttributes<HTMLInputElement>

export const InputText = ({
  register,
  name,
  ...rest
}: InputTextProperties): JSX.Element => {
  const { registerProperties } = useInputText({ register, name })

  const rp = registerProperties as UseFormRegisterReturn | undefined

  return (
    <input
      type="text"
      className={inputStyle}
      {...rest}
      name={name}
      {...(rp ? (rp as unknown as Record<string, unknown>) : {})}
    />
  )
}

// Default export removed — use named export `InputText`
