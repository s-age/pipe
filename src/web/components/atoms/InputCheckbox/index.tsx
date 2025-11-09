import React from 'react'
import type { JSX, InputHTMLAttributes } from 'react'
import type { FieldValues, UseFormRegister } from 'react-hook-form'

import { useInputCheckbox } from './hooks/useInputCheckbox'
import * as styles from './style.css'

type InputCheckboxProperties = {
  label?: React.ReactNode
  register?: UseFormRegister<FieldValues>
  name?: string
} & InputHTMLAttributes<HTMLInputElement>

export const InputCheckbox = ({
  register,
  name,
  label,
  id,
  children,
  ...rest
}: InputCheckboxProperties): JSX.Element => {
  const resolvedLabel = label ?? children

  const { registerProperties, inputId } = useInputCheckbox({
    register,
    name,
    id,
    value: rest.value,
  })

  return (
    <label className={styles.container} htmlFor={inputId}>
      <input
        id={inputId}
        type="checkbox"
        className={styles.hiddenInput}
        {...registerProperties}
        name={name}
        {...rest}
      />
      <span className={styles.control} aria-hidden={true}>
        <svg
          className={styles.svg}
          viewBox="0 0 24 24"
          aria-hidden={true}
          focusable="false"
        >
          <path className={styles.check} d="M20 6L9 17l-5-5" fill="none" />
        </svg>
      </span>
      {resolvedLabel ? <span className={styles.labelText}>{resolvedLabel}</span> : null}
    </label>
  )
}

// (Removed temporary default export) Use named export `InputCheckbox`.
