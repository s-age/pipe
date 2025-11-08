import { useForm } from 'react-hook-form'
import type { UseFormProps, UseFormReturn, FieldValues } from 'react-hook-form'

/**
 * Encapsulate react-hook-form creation logic so the provider and the
 * <Form> component can delegate to a shared hook. This keeps side-effects
 * and initialization in one place and makes the components thinner.
 */
export const useFormMethods = <TFieldValues extends FieldValues = FieldValues>(
  properties?: UseFormProps<TFieldValues>,
): UseFormReturn<TFieldValues> =>
  useForm<TFieldValues>(properties as UseFormProps<TFieldValues>)

export default useFormMethods
