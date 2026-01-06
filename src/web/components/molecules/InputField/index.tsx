import type { JSX } from 'react'
import type { UseControllerProps, FieldValues } from 'react-hook-form'
import { useController } from 'react-hook-form'

import { Label } from '@/components/atoms/Label'
import { InputText } from '@/components/molecules/InputText'
import { useOptionalFormContext } from '@/components/organisms/Form'

import { errorMessageStyle, inputFieldStyle } from './style.css'

type InputFieldProperties<TFieldValues extends FieldValues = FieldValues> = {
  id: string
  label: string
  max?: string
  min?: string
  placeholder?: string
  required?: boolean
  step?: string
  type?: string
} & UseControllerProps<TFieldValues>

export const InputField = <TFieldValues extends FieldValues = FieldValues>({
  id,
  label,
  max,
  min,
  placeholder,
  required,
  step,
  type = 'text',
  ...properties
}: InputFieldProperties<TFieldValues>): JSX.Element => {
  const formContext = useOptionalFormContext<TFieldValues>()
  const {
    field,
    fieldState: { error }
  } = useController({ control: formContext?.control, ...properties })

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
