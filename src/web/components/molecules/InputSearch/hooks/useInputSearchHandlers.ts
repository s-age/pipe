import { useCallback, useMemo } from 'react'
import type { FormEvent, ChangeEvent } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn
} from 'react-hook-form'

import type { FormMethods } from '@/components/organisms/Form'
import { useOptionalFormContext } from '@/components/organisms/Form'

type Properties = {
  value?: string
  onChange?: (value: string) => void
  onSubmit?: (value: string) => void
  register?: UseFormRegister<FieldValues>
  name?: string
}

export const useInputSearchHandlers = ({
  value,
  onChange,
  onSubmit,
  register,
  name
}: Properties): {
  handleSubmit: (event: FormEvent) => void
  handleChange: (event: ChangeEvent<HTMLInputElement>) => void
  registerProperties: Partial<UseFormRegisterReturn>
} => {
  const provider = useOptionalFormContext()

  // Type guard: verify provider has FormMethods structure
  const isFormMethods = (context: unknown): context is FormMethods<FieldValues> =>
    context !== null &&
    typeof context === 'object' &&
    'register' in context &&
    typeof context.register === 'function'

  const registerFunction: UseFormRegister<FieldValues> | undefined =
    register ?? (isFormMethods(provider) ? provider.register : undefined)

  const registerProperties = useMemo<Partial<UseFormRegisterReturn>>(() => {
    if (typeof registerFunction === 'function' && name) {
      try {
        const result = registerFunction(name)
        // Type guard: verify result has UseFormRegisterReturn structure
        if (
          result &&
          typeof result === 'object' &&
          'name' in result &&
          'onChange' in result
        ) {
          return result
        }

        return {}
      } catch {
        return {}
      }
    }

    return {}
  }, [registerFunction, name])

  const handleSubmit = useCallback(
    (event: FormEvent): void => {
      event.preventDefault()
      const submitValue = value ?? ''
      if (onSubmit && typeof submitValue === 'string') {
        onSubmit(submitValue)
      }
    },
    [onSubmit, value]
  )

  const handleChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>): void => {
      if (onChange) onChange(event.target.value)
    },
    [onChange]
  )

  return { handleSubmit, handleChange, registerProperties }
}
