import type { JSX } from 'react'
import type { UseControllerProps, FieldValues } from 'react-hook-form'
import { useController } from 'react-hook-form'

import { InputText } from '@/components/atoms/InputText'
import { Label } from '@/components/atoms/Label'

import { errorMessageStyle, inputFieldStyle } from './style.css'

type InputFieldProperties<TFieldValues extends FieldValues = FieldValues> = {
  label: string
  id: string
  type?: string
  placeholder?: string
  required?: boolean
  min?: string
  max?: string
  step?: string
} & UseControllerProps<TFieldValues>

export const InputField = <TFieldValues extends FieldValues = FieldValues>({
  label,
  id,
  type = 'text',
  placeholder,
  required,
  min,
  max,
  step,
  ...properties
}: InputFieldProperties<TFieldValues>): JSX.Element => {
  const {
    field,
    fieldState: { error }
  } = useController(properties)

  return (
    <div>
      <Label htmlFor={id}>{label}</Label>
      <InputText
        id={id}
        type={type}
        className={inputFieldStyle}
        placeholder={placeholder}
        required={required}
        min={min}
        max={max}
        step={step}
        {...field}
      />
      {error && <p className={errorMessageStyle}>{error.message}</p>}
    </div>
  )
}

// Default export removed — use named export `InputField`
