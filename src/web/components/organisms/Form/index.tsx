import { zodResolver } from '@hookform/resolvers/zod'
import type { ReactNode } from 'react'
import React, { createContext, useContext } from 'react'
import type {
  UseFormProps,
  UseFormReturn,
  FieldValues,
  Resolver
} from 'react-hook-form'
import type { ZodTypeAny } from 'zod'

import { useFormMethods } from './hooks/useFormMethods'
import { formStyle } from './style.css'

export type FormMethods<TFieldValues extends FieldValues = FieldValues> =
  UseFormReturn<TFieldValues>

const FormContext = createContext<FormMethods<FieldValues> | undefined>(undefined)

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

export type FormProperties<TFieldValues extends FieldValues = FieldValues> =
  UseFormProps<TFieldValues> & {
    children: ReactNode
    onSubmit: (data: TFieldValues) => void
    /**
     * Optional Zod schema. When provided and `resolver` is not supplied,
     * the Form will create a zodResolver(schema) internally.
     */
    schema?: ZodTypeAny
  }

export const Form = <TFieldValues extends FieldValues = FieldValues>({
  children,
  onSubmit,
  schema,
  resolver,
  ...properties
}: FormProperties<TFieldValues>): React.JSX.Element => {
  // Resolve which resolver to use. Priority:
  // 1. explicit `resolver` prop
  // 2. if `schema` provided, use zodResolver(schema)
  // 3. otherwise undefined (no resolver)
  const finalResolver =
    resolver ?? (schema ? (zodResolver(schema) as Resolver<TFieldValues>) : undefined)

  // Create form methods here and provide them to descendants.
  // Calling `useFormContext` here would fail because the Provider
  // wrapping the `<form>` would not yet be in scope for this hook.
  const methods = useFormMethods<TFieldValues>({
    ...(properties as UseFormProps<TFieldValues>),
    resolver: finalResolver
  } as UseFormProps<TFieldValues>)

  // If the caller provides `defaultValues` and they change over time (for example
  // when `sessionDetail` is loaded asynchronously), ensure the form is reset so
  // inputs reflect the latest authoritative values. react-hook-form only uses
  // defaultValues on initialization, so we must call `reset` when they change.
  React.useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const dv = (properties as any)?.defaultValues
    if (dv && typeof methods.reset === 'function') {
      methods.reset(dv)
    }
    // We intentionally only depend on the defaultValues reference. The caller
    // should pass a stable memoized object (useMemo) when possible.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [(properties as UseFormProps<TFieldValues>)?.defaultValues])

  return (
    <FormContext.Provider value={methods as FormMethods<FieldValues>}>
      <form className={formStyle} onSubmit={methods.handleSubmit(onSubmit)}>
        {children}
      </form>
    </FormContext.Provider>
  )
}
