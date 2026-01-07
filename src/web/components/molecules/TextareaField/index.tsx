import type { JSX } from 'react'
import type { UseControllerProps, FieldValues } from 'react-hook-form'
import { useController } from 'react-hook-form'

import { Label } from '@/components/atoms/Label'
import { FlexColumn } from '@/components/molecules/FlexColumn'
import { Paragraph } from '@/components/molecules/Paragraph'
import { TextArea } from '@/components/molecules/TextArea'
import { useOptionalFormContext } from '@/components/organisms/Form'

import { errorMessageStyle } from './style.css'

type TextareaFieldProperties<TFieldValues extends FieldValues = FieldValues> = {
  id: string
  label: string
  placeholder?: string
  readOnly?: boolean
  required?: boolean
} & UseControllerProps<TFieldValues>

export const TextareaField = <TFieldValues extends FieldValues = FieldValues>({
  id,
  label,
  placeholder,
  readOnly,
  required,
  ...properties
}: TextareaFieldProperties<TFieldValues>): JSX.Element => {
  const formContext = useOptionalFormContext<TFieldValues>()
  const {
    field,
    fieldState: { error }
  } = useController({ control: formContext?.control, ...properties })

  return (
    <FlexColumn>
      <Label htmlFor={id}>{label}</Label>
      <TextArea
        id={id}
        placeholder={placeholder}
        readOnly={readOnly}
        required={required}
        {...field}
      />
      {error && <Paragraph className={errorMessageStyle}>{error.message}</Paragraph>}
    </FlexColumn>
  )
}

// Default export removed — use named export `TextareaField`

// Default export removed — use named export `TextareaField`
