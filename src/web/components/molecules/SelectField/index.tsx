import { JSX } from 'react'
import { useController, UseControllerProps, FieldValues } from 'react-hook-form'

import Label from '@/components/atoms/Label'
import Select from '@/components/atoms/Select'

import { errorMessageStyle } from './style.css'

type SelectOption = {
  value: string
  label: string
}

type SelectFieldProps<TFieldValues extends FieldValues = FieldValues> = {
  label: string
  id: string
  options: SelectOption[]
} & UseControllerProps<TFieldValues>

const SelectField = <TFieldValues extends FieldValues = FieldValues>({
  label,
  id,
  options,
  ...props
}: SelectFieldProps<TFieldValues>): JSX.Element => {
  const {
    field,
    fieldState: { error },
  } = useController(props)

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

export default SelectField
