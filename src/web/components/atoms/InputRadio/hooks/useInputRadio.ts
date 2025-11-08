import { useMemo, useId } from 'react'
import type { InputHTMLAttributes } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn,
} from 'react-hook-form'

import type { FormMethods } from '@/components/organisms/Form'
import { useOptionalFormContext } from '@/components/organisms/Form'

type UseInputRadioProperties = {
  register?: UseFormRegister<FieldValues>
  name?: string
  id?: string
  value?: InputHTMLAttributes<HTMLInputElement>['value']
}

export const useInputRadio = ({
  register,
  name,
  id,
  value,
}: UseInputRadioProperties): {
  registerProperties: Partial<UseFormRegisterReturn>
  inputId: string
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

export default useInputRadio
