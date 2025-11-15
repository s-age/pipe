import type { JSX } from 'react'
import type { UseControllerProps, FieldValues } from 'react-hook-form'
import { useController } from 'react-hook-form'

import { Label } from '@/components/atoms/Label'
import { Select } from '@/components/molecules/Select'
import { useOptionalFormContext } from '@/components/organisms/Form'

import { errorMessageStyle } from './style.css'

type SelectOption = {
  value: string
  label: string
}

type SelectFieldProperties<TFieldValues extends FieldValues = FieldValues> = {
  label: string
  id: string
  options: SelectOption[]
} & UseControllerProps<TFieldValues>

export const SelectField = <TFieldValues extends FieldValues = FieldValues>({
  label,
  id,
  options,
  ...properties
}: SelectFieldProperties<TFieldValues>): JSX.Element => {
  const formContext = useOptionalFormContext<TFieldValues>()
  const {
    field,
    fieldState: { error }
  } = useController({ control: formContext?.control, ...properties })

  return (
    <div>
      <Label htmlFor={id}>{label}</Label>
      <Select id={id} {...field}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </Select>
      {error && <p className={errorMessageStyle}>{error.message}</p>}
    </div>
  )
}

// Default export removed — use named export `SelectField`
