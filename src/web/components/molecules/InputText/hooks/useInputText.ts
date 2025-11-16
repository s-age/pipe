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

  // provider and props are available here

  const registerFunction: UseFormRegister<FieldValues> | undefined =
    register ?? provider?.register

  // registerFunction resolved from props or provider

  const registerProperties = useMemo<Partial<UseFormRegisterReturn>>(() => {
    if (typeof registerFunction === 'function' && name) {
      try {
        const rp = registerFunction(name) as UseFormRegisterReturn
        // registerProperties.ref is available
        // Wrap the returned registerProperties.onChange to add a debug log
        const wrapped: UseFormRegisterReturn = {
          ...rp,
          onChange: ((event: unknown) => {
            try {
              ;(rp.onChange as unknown as (...arguments_: unknown[]) => void)?.(
                event as unknown
              )
            } catch {
              // ignore
            }

            // Best-effort extract value and also call provider.setValue as a fallback
            const value = (event as unknown as { target?: { value?: unknown } })?.target
              ?.value as unknown as string | undefined

            // onChange debug suppressed

            try {
              if (provider && typeof provider.setValue === 'function' && name) {
                provider.setValue(name, value ?? '')
              }
            } catch {
              // ignore
            }
          }) as UseFormRegisterReturn['onChange']
        }

        // registerProperties returned by register function

        return wrapped
      } catch {
        return {}
      }
    }

    return {}
  }, [registerFunction, name, provider])

  return { registerProperties }
}
