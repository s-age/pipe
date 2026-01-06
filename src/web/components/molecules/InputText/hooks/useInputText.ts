import { useMemo } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn
} from 'react-hook-form'

import type { FormMethods } from '@/components/organisms/Form'
import { useOptionalFormContext } from '@/components/organisms/Form'

type UseInputTextProperties = {
  name?: string
  register?: UseFormRegister<FieldValues>
}

export const useInputText = ({
  name,
  register
}: UseInputTextProperties): {
  registerProperties: Partial<UseFormRegisterReturn>
} => {
  const provider = useOptionalFormContext() as FormMethods<FieldValues> | undefined

  const registerFunction: UseFormRegister<FieldValues> | undefined =
    register ?? provider?.register

  const registerProperties = useMemo<Partial<UseFormRegisterReturn>>(() => {
    if (typeof registerFunction === 'function' && name) {
      try {
        const rp = registerFunction(name) as UseFormRegisterReturn

        return rp
      } catch {
        return {}
      }
    }

    return {}
  }, [registerFunction, name])

  return { registerProperties }
}
