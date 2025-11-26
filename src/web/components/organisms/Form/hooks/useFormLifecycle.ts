import { useEffect } from 'react'
import type { UseFormReturn, FieldValues, DefaultValues } from 'react-hook-form'

export const useFormLifecycle = <TFieldValues extends FieldValues>(
  methods: UseFormReturn<TFieldValues>,
  defaultValues?: DefaultValues<TFieldValues>
): void => {
  useEffect(() => {
    if (defaultValues) {
      methods.reset(defaultValues)
    }
  }, [defaultValues, methods, methods.reset])
}
