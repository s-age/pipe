import type {
  FieldValues,
  Path,
  RegisterOptions,
  UseFormRegisterReturn,
  UseFormReturn
} from 'react-hook-form'

import type { FormMethods } from '../FormContext'

/**
 * Patches form methods to provide central interception of field changes.
 * This wraps the `register` function to allow observation and augmentation
 * of onChange events without requiring callers to change how they use the hook.
 *
 * @param methods - The form methods returned from useForm
 * @returns Patched form methods with wrapped register function
 */
export const useFormMethodsPatcher = <TFieldValues extends FieldValues>(
  methods: UseFormReturn<TFieldValues>
): FormMethods<TFieldValues> => {
  const patchedRegister = (
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
        // Swallow errors from user-provided handlers to avoid breaking flow
        // but surface debug info in development
        if (process.env.NODE_ENV !== 'production') {
          // eslint-disable-next-line no-console
          console.error(error)
        }
      }
    }

    return methods.register(name, {
      ...options,
      onChange: wrappedOnChange
    })
  }

  return {
    ...methods,
    register: patchedRegister
  } as FormMethods<TFieldValues>
}
