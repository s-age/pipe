import { useCallback, useId, useMemo } from 'react'
import type { TextareaHTMLAttributes } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn
} from 'react-hook-form'

import { useOptionalFormContext } from '@/components/organisms/Form'

export type UseTextAreaProperties = Omit<
  TextareaHTMLAttributes<HTMLTextAreaElement>,
  'onChange'
> & {
  value: string
  id?: string
  name?: string
  register?: UseFormRegister<FieldValues>
  onChange?: (value: string) => void
}

export type UseTextAreaReturn = {
  id: string
  visibleValue: string
  registerProperties?: UseFormRegisterReturn | undefined
  handleChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void
}

export const useTextArea = ({
  id: idProperty,
  name,
  onChange,
  register,
  value: controlledValue
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
      // call register onChange if present
      registerProperties?.onChange?.(event as unknown as Event)

      onChange?.(v)
    },
    [onChange, registerProperties]
  )

  const visibleValue = controlledValue

  return {
    id: resolvedId,
    registerProperties,
    visibleValue,
    handleChange
  }
}
