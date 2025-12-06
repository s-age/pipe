import { zodResolver } from '@hookform/resolvers/zod'
import type { ReactNode } from 'react'
import React from 'react'
import { useForm } from 'react-hook-form'
import type {
  UseFormProps,
  FieldValues,
  Resolver,
  RegisterOptions,
  UseFormRegisterReturn,
  Path,
  UseFormReturn
} from 'react-hook-form'
import type { ZodTypeAny } from 'zod'

import { FormContext } from './FormContext'
import type { FormMethods } from './FormContext'
import { useFormHandlers } from './hooks/useFormHandlers'
import { useFormLifecycle } from './hooks/useFormLifecycle'
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

  // Reset form when defaultValues change
  useFormLifecycle(
    methods,
    typeof properties.defaultValues === 'object' ? properties.defaultValues : undefined
  )

  const { handleFormSubmit } = useFormHandlers()

  // Patch the methods to allow central interception of field changes.
  // This wraps `register` so callers don't need to change how they use the
  // hook, but `onChange` can be observed/augmented here.
  const patchedMethods = ((): FormMethods<TFieldValues> => {
    // Keep original methods reference
    const originalMethods = methods as UseFormReturn<TFieldValues>

    const register = (
      name: Path<TFieldValues>,
      options?: RegisterOptions<TFieldValues>
    ): UseFormRegisterReturn => {
      const wrappedOnChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
        // Central trap point for all field onChange events.
        // Place logging, analytics, or additional handling here.
        // Example: console.debug('Form field changed', name, event)
        try {
          options?.onChange?.(event)
        } catch (error) {
          // swallow errors from user-provided handlers to avoid breaking flow
          // but surface debug info in development
          // eslint-disable-next-line no-console
          if (process.env.NODE_ENV !== 'production') console.error(error)
        }
      }

      return originalMethods.register(name, {
        ...options,
        onChange: wrappedOnChange
      })
    }

    return { ...(methods as object), register } as FormMethods<TFieldValues>
  })()

  return (
    <FormContext.Provider value={patchedMethods as FormMethods<FieldValues>}>
      <form className={formStyle} onSubmit={handleFormSubmit}>
        {children}
      </form>
    </FormContext.Provider>
  )
}
