import { createContext } from 'react'
import type { FieldValues, UseFormReturn } from 'react-hook-form'

export type FormMethods<TFieldValues extends FieldValues = FieldValues> =
  UseFormReturn<TFieldValues>

export const FormContext = createContext<FormMethods<FieldValues> | undefined>(
  undefined
)

export { useFormContext, useOptionalFormContext } from './hooks/useFormContext'
