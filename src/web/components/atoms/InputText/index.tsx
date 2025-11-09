import type { InputHTMLAttributes, JSX } from 'react'
import type { FieldValues, UseFormRegister } from 'react-hook-form'

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

  return (
    <input
      type="text"
      className={inputStyle}
      {...registerProperties}
      {...rest}
      name={name}
    />
  )
}

// Default export removed — use named export `InputText`
