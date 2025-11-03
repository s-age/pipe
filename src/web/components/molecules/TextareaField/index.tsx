import { JSX } from 'react'
import { useController, UseControllerProps, FieldValues } from 'react-hook-form'

import Label from '@/components/atoms/Label'
import TextArea from '@/components/atoms/TextArea'

import { errorMessageStyle } from './style.css'

type TextareaFieldProps<TFieldValues extends FieldValues = FieldValues> = {
  label: string
  id: string
  placeholder?: string
  readOnly?: boolean
  required?: boolean
} & UseControllerProps<TFieldValues>

const TextareaField = <TFieldValues extends FieldValues = FieldValues>({
  label,
  id,
  placeholder,
  readOnly,
  required,
  ...props
}: TextareaFieldProps<TFieldValues>): JSX.Element => {
  const {
    field,
    fieldState: { error },
  } = useController(props)

  return (
    <div>
      <Label htmlFor={id}>{label}</Label>
      <TextArea
        id={id}
        placeholder={placeholder}
        readOnly={readOnly}
        required={required}
        {...field}
      />
      {error && <p className={errorMessageStyle}>{error.message}</p>}
    </div>
  )
}

export default TextareaField
