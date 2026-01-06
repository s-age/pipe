import React from 'react'
import type { InputHTMLAttributes, JSX } from 'react'
import type { FieldValues, UseFormRegister } from 'react-hook-form'

import { useInputRadio } from './hooks/useInputRadio'
import * as styles from './style.css'

type InputRadioProperties = {
  label?: React.ReactNode
  name?: string
  register?: UseFormRegister<FieldValues>
} & InputHTMLAttributes<HTMLInputElement>

export const InputRadio = ({
  children,
  id,
  label,
  name,
  register,
  ...rest
}: InputRadioProperties): JSX.Element => {
  const resolvedLabel = label ?? children

  const { inputId, registerProperties } = useInputRadio({
    register,
    name,
    id,
    value: rest.value
  })

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
      <span className={styles.control} aria-hidden={true}>
        <svg
          className={styles.svg}
          viewBox="0 0 24 24"
          aria-hidden={true}
          focusable="false"
        >
          <circle cx="12" cy="12" r="5" fill="transparent" />
        </svg>
      </span>
      {resolvedLabel ? <span className={styles.labelText}>{resolvedLabel}</span> : null}
    </label>
  )
}

// (Removed temporary default export) Use named export `InputRadio`.
