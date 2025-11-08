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

type InputCheckboxProps = {
  label?: React.ReactNode
  register?: UseFormRegister<FieldValues>
  name?: string
} & InputHTMLAttributes<HTMLInputElement>

const InputCheckbox = ({
  register,
  name,
  label,
  id,
  ...rest
}: InputCheckboxProps): JSX.Element => {
  // Try to obtain register from provider if present. useRHFFormContext throws when no provider,
  // so call it inside try/catch to avoid runtime error and fall back to undefined.
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
        type="checkbox"
        className={styles.hiddenInput}
        {...registerProps}
        name={name}
        {...rest}
      />
      <span className={styles.control} aria-hidden>
        <svg className={styles.svg} viewBox="0 0 24 24" aria-hidden focusable="false">
          <path className={styles.check} d="M20 6L9 17l-5-5" fill="none" />
        </svg>
      </span>
      {label ? <span className={styles.labelText}>{label}</span> : null}
    </label>
  )
}

export default InputCheckbox
