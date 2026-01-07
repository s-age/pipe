import type { JSX } from 'react'
import type { UseControllerProps, FieldValues } from 'react-hook-form'
import { useController } from 'react-hook-form'

import { Label } from '@/components/atoms/Label'
import { FlexColumn } from '@/components/molecules/FlexColumn'
import { Paragraph } from '@/components/molecules/Paragraph'
import { Select } from '@/components/molecules/Select'
import { useOptionalFormContext } from '@/components/organisms/Form'

import { errorMessageStyle } from './style.css'

type SelectOption = {
  label: string
  value: string
}

type SelectFieldProperties<TFieldValues extends FieldValues = FieldValues> = {
  id: string
  label: string
  options: SelectOption[]
} & UseControllerProps<TFieldValues>

export const SelectField = <TFieldValues extends FieldValues = FieldValues>({
  id,
  label,
  options,
  ...properties
}: SelectFieldProperties<TFieldValues>): JSX.Element => {
  const formContext = useOptionalFormContext<TFieldValues>()
  const {
    field,
    fieldState: { error }
  } = useController({ control: formContext?.control, ...properties })

  return (
    <FlexColumn>
      <Label htmlFor={id}>{label}</Label>
      <Select id={id} {...field}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </Select>
      {error && <Paragraph className={errorMessageStyle}>{error.message}</Paragraph>}
    </FlexColumn>
  )
}

// Default export removed — use named export `SelectField`
