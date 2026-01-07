import React from 'react'
import type { JSX, InputHTMLAttributes } from 'react'
import type { FieldValues, UseFormRegister } from 'react-hook-form'

import { Box } from '@/components/molecules/Box'
import { Flex } from '@/components/molecules/Flex'

import { useInputCheckbox } from './hooks/useInputCheckbox'
import * as styles from './style.css'

type InputCheckboxProperties = {
  label?: React.ReactNode
  name?: string
  register?: UseFormRegister<FieldValues>
} & InputHTMLAttributes<HTMLInputElement>

export const InputCheckbox = ({
  children,
  id,
  label,
  name,
  register,
  ...rest
}: InputCheckboxProperties): JSX.Element => {
  const resolvedLabel = label ?? children

  const { inputId, registerProperties } = useInputCheckbox({
    register,
    name,
    id,
    value: rest.value
  })

  return (
    <Flex as="label" className={styles.container} htmlFor={inputId}>
      <input
        id={inputId}
        type="checkbox"
        className={styles.hiddenInput}
        {...registerProperties}
        name={name}
        {...rest}
      />
      <Box className={styles.control} aria-hidden={true}>
        <svg
          className={styles.svg}
          viewBox="0 0 24 24"
          aria-hidden={true}
          focusable="false"
        >
          <path className={styles.check} d="M20 6L9 17l-5-5" fill="none" />
        </svg>
      </Box>
      {resolvedLabel ? (
        <Box as="span" className={styles.labelText}>
          {resolvedLabel}
        </Box>
      ) : null}
    </Flex>
  )
}

// (Removed temporary default export) Use named export `InputCheckbox`.
