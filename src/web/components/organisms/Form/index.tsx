import { zodResolver } from '@hookform/resolvers/zod'
import type { ReactNode } from 'react'
import React from 'react'
import { useForm } from 'react-hook-form'
import type { UseFormProps, FieldValues, Resolver } from 'react-hook-form'
import type { ZodTypeAny } from 'zod'

import { FormContext } from './FormContext'
import type { FormMethods } from './FormContext'
import { useFormHandlers } from './hooks/useFormHandlers'
import { formStyle } from './style.css'

export { useFormContext, useOptionalFormContext } from './FormContext'
export type { FormMethods } from './FormContext'

export type FormProperties<TFieldValues extends FieldValues = FieldValues> =
  UseFormProps<TFieldValues> & {
    children: ReactNode
    /**
     * Optional Zod schema. When provided and `resolver` is not supplied,
     * the Form will create a zodResolver(schema) internally.
     */
    schema?: ZodTypeAny
  }

export const Form = <TFieldValues extends FieldValues = FieldValues>({
  children,
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
  const methods = useForm<TFieldValues>({
    ...(properties as UseFormProps<TFieldValues>),
    resolver: finalResolver
  } as UseFormProps<TFieldValues>)

  const { handleFormSubmit } = useFormHandlers()

  // If the caller provides `defaultValues` and they change over time (for example
  // when `sessionDetail` is loaded asynchronously), ensure the form is reset so
  // inputs reflect the latest authoritative values. react-hook-form only uses
  // defaultValues on initialization, so we must call `reset` when they change.
  React.useEffect(() => {
    const dv = (properties as UseFormProps<TFieldValues>)?.defaultValues as
      | TFieldValues
      | undefined
    if (dv && typeof methods.reset === 'function') {
      // guard: consider reset

      try {
        // Guard: avoid resetting if the current form values already match the
        // provided defaultValues. This prevents accidental clears when a
        // defaultValues object reference changes during user input.
        // Use a JSON stringify comparison for a lightweight deep-equality
        // check; this is acceptable for debugging/guarding here.

        const currentValues: unknown = methods.getValues
          ? methods.getValues()
          : undefined
        const shouldReset = ((): boolean => {
          try {
            return JSON.stringify(currentValues) !== JSON.stringify(dv)
          } catch {
            return true
          }
        })()

        if (shouldReset) {
          methods.reset(dv)
        }
      } catch {
        // Fallback: if any error occurs, call reset to preserve previous behavior
        try {
          methods.reset(dv)
        } catch {
          // ignore
        }
      }
    }
    // We intentionally only depend on the defaultValues reference. The caller
    // should pass a stable memoized object (useMemo) when possible.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [(properties as UseFormProps<TFieldValues>)?.defaultValues])

  // Log validation errors to console
  React.useEffect(() => {
    const errors = methods.formState.errors
    if (errors && Object.keys(errors).length > 0) {
      console.error('Form validation errors:', errors)
    }
  }, [methods.formState.errors])

  return (
    <FormContext.Provider value={methods as FormMethods<FieldValues>}>
      <form className={formStyle} onSubmit={handleFormSubmit}>
        {children}
      </form>
    </FormContext.Provider>
  )
}
