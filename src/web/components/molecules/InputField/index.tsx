import { JSX } from 'react'
import { useController, UseControllerProps, FieldValues } from 'react-hook-form'

import InputText from '@/components/atoms/InputText'
import Label from '@/components/atoms/Label'

import { errorMessageStyle, inputFieldStyle } from './style.css'

type InputFieldProps<TFieldValues extends FieldValues = FieldValues> = {
  label: string
  id: string
  type?: string
  placeholder?: string
  required?: boolean
  min?: string
  max?: string
  step?: string
} & UseControllerProps<TFieldValues>

const InputField = <TFieldValues extends FieldValues = FieldValues>({
  label,
  id,
  type = 'text',
  placeholder,
  required,
  min,
  max,
  step,
  ...props
}: InputFieldProps<TFieldValues>): JSX.Element => {
  const {
    field,
    fieldState: { error },
  } = useController(props)

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

export default InputField
