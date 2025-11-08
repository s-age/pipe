import React, { InputHTMLAttributes, useMemo, JSX, useId } from 'react'

import * as styles from './style.css'
import {
  FormMethods,
  useFormContext as useRHFFormContext,
} from '@/components/organisms/Form'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn,
} from 'react-hook-form'

type InputRadioProps = {
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
}: InputRadioProps): JSX.Element => {
  let provider: FormMethods<FieldValues> | undefined
  try {
    provider = useRHFFormContext()
  } catch (error) {
    provider = undefined
  }

  const registerFn: UseFormRegister<FieldValues> | undefined =
    register ?? provider?.register

  const registerProps = useMemo<Partial<UseFormRegisterReturn>>(() => {
    if (typeof registerFn === 'function' && name) {
      try {
        return registerFn(name) as UseFormRegisterReturn
      } catch (error) {
        // register may throw in some edge cases; fall back
        return {}
      }
    }
    return {}
  }, [registerFn, name])

  const reactId = useId()
  const valueProp = rest.value as string | number | undefined
  const inputId =
    id ??
    (typeof name === 'string' && valueProp ? `${name}-${String(valueProp)}` : reactId)

  return (
    <label className={styles.container} htmlFor={inputId}>
      <input
        id={inputId}
        type="radio"
        className={styles.hiddenInput}
        {...registerProps}
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
