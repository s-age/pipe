import { useMemo, useId } from 'react'
import type { InputHTMLAttributes } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn
} from 'react-hook-form'

import type { FormMethods } from '@/components/organisms/Form'
import { useOptionalFormContext } from '@/components/organisms/Form'

type UseInputRadioProperties = {
  id?: string
  name?: string
  register?: UseFormRegister<FieldValues>
  value?: InputHTMLAttributes<HTMLInputElement>['value']
}

export const useInputRadio = ({
  id,
  name,
  register,
  value
}: UseInputRadioProperties): {
  inputId: string
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

  const reactId = useId()
  const valueProperty = value as string | number | undefined
  const inputId =
    id ??
    (typeof name === 'string' && valueProperty
      ? `${name}-${String(valueProperty)}`
      : reactId)

  return { registerProperties, inputId }
}

// (Removed temporary default export) Use named export `useInputRadio`.
