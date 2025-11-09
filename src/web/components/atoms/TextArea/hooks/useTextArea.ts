import { useCallback, useId, useMemo } from 'react'
import type { TextareaHTMLAttributes } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn,
} from 'react-hook-form'

import { useOptionalFormContext } from '@/components/organisms/Form'

export type UseTextAreaProperties = Omit<
  TextareaHTMLAttributes<HTMLTextAreaElement>,
  'onChange'
> & {
  value: string
  onChange?: (value: string) => void
  register?: UseFormRegister<FieldValues>
  name?: string
  id?: string
}

export type UseTextAreaReturn = {
  id: string
  registerProperties?: UseFormRegisterReturn | undefined
  visibleValue: string
  handleChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void
}

export const useTextArea = ({
  value: controlledValue,
  onChange,
  register,
  name,
  id: idProperty,
}: UseTextAreaProperties): UseTextAreaReturn => {
  const fallbackId = useId()
  const resolvedId =
    idProperty ?? (name ? `${name}-textarea` : `textarea-${fallbackId}`)

  const providerRegister: UseFormRegister<FieldValues> | undefined =
    useOptionalFormContext()?.register

  const registerProperties = useMemo<UseFormRegisterReturn | undefined>(() => {
    if (!name) return undefined
    if (register) return register(name)
    if (providerRegister) return providerRegister(name)

    return undefined
  }, [register, providerRegister, name])

  const handleChange = useCallback(
    (event: React.ChangeEvent<HTMLTextAreaElement>) => {
      const v = event.target.value
      try {
        registerProperties?.onChange?.(event as unknown as Event)
      } catch {
        // ignore
      }
      onChange?.(v)
    },
    [onChange, registerProperties],
  )

  const visibleValue = controlledValue

  return {
    id: resolvedId,
    registerProperties,
    visibleValue,
    handleChange,
  }
}

// (Removed temporary default export) Use named export `useTextArea`.
