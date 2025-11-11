import type { JSX } from 'react'
import type { UseControllerProps, FieldValues } from 'react-hook-form'
import { useController } from 'react-hook-form'

import { Label } from '@/components/atoms/Label'
import { TextArea } from '@/components/molecules/TextArea'

import { errorMessageStyle } from './style.css'

type TextareaFieldProperties<TFieldValues extends FieldValues = FieldValues> = {
  label: string
  id: string
  placeholder?: string
  readOnly?: boolean
  required?: boolean
} & UseControllerProps<TFieldValues>

export const TextareaField = <TFieldValues extends FieldValues = FieldValues>({
  label,
  id,
  placeholder,
  readOnly,
  required,
  ...properties
}: TextareaFieldProperties<TFieldValues>): JSX.Element => {
  const {
    field,
    fieldState: { error }
  } = useController(properties)

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

// Default export removed — use named export `TextareaField`
