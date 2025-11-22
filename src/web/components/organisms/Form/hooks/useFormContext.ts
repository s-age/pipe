import { useContext } from 'react'
import type { FieldValues } from 'react-hook-form'

import { FormContext } from '../FormContext'
import type { FormMethods } from '../FormContext'

export const useFormContext = <
  TFieldValues extends FieldValues = FieldValues
>(): FormMethods<TFieldValues> => {
  const context = useContext(FormContext)
  if (context === undefined) {
    throw new Error('useFormContext must be used within a Form')
  }

  return context as FormMethods<TFieldValues>
}

// A safe variant that returns undefined when no provider is present.
export const useOptionalFormContext = <
  TFieldValues extends FieldValues = FieldValues
>(): FormMethods<TFieldValues> | undefined =>
  useContext(FormContext) as FormMethods<TFieldValues> | undefined
