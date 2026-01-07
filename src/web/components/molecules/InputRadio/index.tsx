import React from 'react'
import type { InputHTMLAttributes, JSX } from 'react'
import type { FieldValues, UseFormRegister } from 'react-hook-form'

import { Box } from '@/components/molecules/Box'
import { Flex } from '@/components/molecules/Flex'

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
    <Flex as="label" className={styles.container} htmlFor={inputId}>
      <input
        id={inputId}
        type="radio"
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
          <circle cx="12" cy="12" r="5" fill="transparent" />
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

// (Removed temporary default export) Use named export `InputRadio`.
