import type { InputHTMLAttributes, JSX } from 'react'
import React, { useMemo, useId } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn,
} from 'react-hook-form'

import type { FormMethods } from '@/components/organisms/Form'
import { useOptionalFormContext } from '@/components/organisms/Form'

import * as styles from './style.css'

type InputRadioProperties = {
  label?: React.ReactNode
  register?: UseFormRegister<FieldValues>
  name?: string
} & InputHTMLAttributes<HTMLInputElement>

const InputRadio = ({
  register,
  name,
  label,
  id,
  ...rest
}: InputRadioProperties): JSX.Element => {
  const provider = useOptionalFormContext() as FormMethods<FieldValues> | undefined

  const registerFunction: UseFormRegister<FieldValues> | undefined =
    register ?? provider?.register

  const registerProperties = useMemo<Partial<UseFormRegisterReturn>>(() => {
    if (typeof registerFunction === 'function' && name) {
      try {
        return registerFunction(name) as UseFormRegisterReturn
      } catch {
        // register may throw in some edge cases; fall back
        return {}
      }
    }

    return {}
  }, [registerFunction, name])

  const reactId = useId()
  const valueProperty = rest.value as string | number | undefined
  const inputId =
    id ??
    (typeof name === 'string' && valueProperty
      ? `${name}-${String(valueProperty)}`
      : reactId)

  return (
    <label className={styles.container} htmlFor={inputId}>
      <input
        id={inputId}
        type="radio"
        className={styles.hiddenInput}
        {...registerProperties}
        name={name}
        {...rest}
      />
      <span className={styles.control} aria-hidden>
        <svg className={styles.svg} viewBox="0 0 24 24" aria-hidden focusable="false">
          <circle cx="12" cy="12" r="5" fill="transparent" />
        </svg>
      </span>
      {label ? <span className={styles.labelText}>{label}</span> : null}
    </label>
  )
}

export default InputRadio
