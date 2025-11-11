import { createContext, useContext } from 'react'
import type { UseFormReturn, FieldValues } from 'react-hook-form'

export type FormMethods<TFieldValues extends FieldValues = FieldValues> =
  UseFormReturn<TFieldValues>

export const FormContext = createContext<FormMethods<FieldValues> | undefined>(
  undefined
)

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
