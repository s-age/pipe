import type { JSX } from 'react'
import type { UseControllerProps, FieldValues } from 'react-hook-form'
import { useController } from 'react-hook-form'

import { Label } from '@/components/atoms/Label'
import { InputCheckbox } from '@/components/molecules/InputCheckbox'

import { checkboxContainer, labelStyle } from './style.css'

type CheckboxFieldProperties<TFieldValues extends FieldValues = FieldValues> = {
  label: string
  id: string
} & UseControllerProps<TFieldValues>

export const CheckboxField = <TFieldValues extends FieldValues = FieldValues>({
  label,
  id,
  ...properties
}: CheckboxFieldProperties<TFieldValues>): JSX.Element => {
  const { field } = useController(properties)

  return (
    <div className={checkboxContainer}>
      <InputCheckbox
        id={id}
        checked={field.value}
        onChange={field.onChange}
        onBlur={field.onBlur}
        name={field.name}
      />
      <Label htmlFor={id} className={labelStyle}>
        {label}
      </Label>
    </div>
  )
}

// Default export removed — use named export `CheckboxField`
