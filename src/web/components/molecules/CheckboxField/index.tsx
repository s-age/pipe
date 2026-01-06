import type { JSX } from 'react'
import type { UseControllerProps, FieldValues } from 'react-hook-form'
import { useController } from 'react-hook-form'

import { Label } from '@/components/atoms/Label'
import { InputCheckbox } from '@/components/molecules/InputCheckbox'
import { useOptionalFormContext } from '@/components/organisms/Form'

import { checkboxContainer, labelStyle } from './style.css'

type CheckboxFieldProperties<TFieldValues extends FieldValues = FieldValues> = {
  id: string
  label: string
} & UseControllerProps<TFieldValues>

export const CheckboxField = <TFieldValues extends FieldValues = FieldValues>({
  id,
  label,
  ...properties
}: CheckboxFieldProperties<TFieldValues>): JSX.Element => {
  const formContext = useOptionalFormContext<TFieldValues>()
  const { field } = useController({ control: formContext?.control, ...properties })

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
