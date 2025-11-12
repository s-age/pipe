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

export const useInputSearch = ({
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
  const provider = useOptionalFormContext() as FormMethods<FieldValues> | undefined

  const registerFunction: UseFormRegister<FieldValues> | undefined =
    register ?? provider?.register

  const registerProperties = useMemo<Partial<UseFormRegisterReturn>>(() => {
    if (typeof registerFunction === 'function' && name) {
      try {
        return registerFunction(name) as UseFormRegisterReturn
      } catch {
        return {}
      }
    }

    return {}
  }, [registerFunction, name])

  const handleSubmit = useCallback(
    (event: FormEvent): void => {
      event.preventDefault()
      if (onSubmit) onSubmit((value ?? '') as string)
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
