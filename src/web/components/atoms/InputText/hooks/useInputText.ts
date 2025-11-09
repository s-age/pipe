import { useMemo } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn
} from 'react-hook-form'

import type { FormMethods } from '@/components/organisms/Form'
import { useOptionalFormContext } from '@/components/organisms/Form'

type UseInputTextProperties = {
  register?: UseFormRegister<FieldValues>
  name?: string
}

export const useInputText = ({
  register,
  name
}: UseInputTextProperties): {
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

  return { registerProperties }
}

// Default export removed — use named export `useInputText`
