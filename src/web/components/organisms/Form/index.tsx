import type { ReactNode } from 'react'
import React, { createContext, useContext } from 'react'
import type { UseFormProps, UseFormReturn, FieldValues } from 'react-hook-form'
import { useForm } from 'react-hook-form'

export type FormMethods<TFieldValues extends FieldValues = FieldValues> =
  UseFormReturn<TFieldValues>

const FormContext = createContext<FormMethods<FieldValues> | undefined>(undefined)

export type FormProviderProperties<TFieldValues extends FieldValues = FieldValues> =
  UseFormProps<TFieldValues> & {
    children: ReactNode
  }

export const FormProvider = <TFieldValues extends FieldValues = FieldValues>({
  children,
  ...properties
}: FormProviderProperties<TFieldValues>): React.JSX.Element => {
  const methods = useForm<TFieldValues>(properties as UseFormProps<TFieldValues>)

  return (
    <FormContext.Provider value={methods as FormMethods<FieldValues>}>
      {children}
    </FormContext.Provider>
  )
}

export const useFormContext = <
  TFieldValues extends FieldValues = FieldValues,
>(): FormMethods<TFieldValues> => {
  const context = useContext(FormContext)
  if (context === undefined) {
    throw new Error('useFormContext must be used within a FormProvider')
  }

  return context as FormMethods<TFieldValues>
}

// A safe variant that returns undefined when no provider is present.
export const useOptionalFormContext = <
  TFieldValues extends FieldValues = FieldValues,
>(): FormMethods<TFieldValues> | undefined =>
  useContext(FormContext) as FormMethods<TFieldValues> | undefined

export type FormProperties<TFieldValues extends FieldValues = FieldValues> =
  UseFormProps<TFieldValues> & {
    children: ReactNode
    onSubmit: (data: TFieldValues) => void
  }

export const Form = <TFieldValues extends FieldValues = FieldValues>({
  children,
  onSubmit,
  ...properties
}: FormProperties<TFieldValues>): React.JSX.Element => {
  // Create form methods here and provide them to descendants.
  // Calling `useFormContext` here would fail because the Provider
  // wrapping the `<form>` would not yet be in scope for this hook.
  const methods = useForm<TFieldValues>(properties as UseFormProps<TFieldValues>)

  return (
    <FormContext.Provider value={methods as FormMethods<FieldValues>}>
      <form onSubmit={methods.handleSubmit(onSubmit)}>{children}</form>
    </FormContext.Provider>
  )
}
