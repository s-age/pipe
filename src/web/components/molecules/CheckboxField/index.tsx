import type { JSX } from 'react'
import type { UseControllerProps, FieldValues } from 'react-hook-form'
import { useController } from 'react-hook-form'

import Checkbox from '@/components/atoms/Checkbox'
import Label from '@/components/atoms/Label'

import { checkboxContainer, labelStyle } from './style.css'

type CheckboxFieldProperties<TFieldValues extends FieldValues = FieldValues> = {
  label: string
  id: string
} & UseControllerProps<TFieldValues>

const CheckboxField = <TFieldValues extends FieldValues = FieldValues>({
  label,
  id,
  ...properties
}: CheckboxFieldProperties<TFieldValues>): JSX.Element => {
  const { field } = useController(properties)

  return (
    <div className={checkboxContainer}>
      <Checkbox
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

export default CheckboxField
