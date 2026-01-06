import type { JSX } from 'react'
import type { FieldError } from 'react-hook-form'

import { errorMessageStyle } from './style.css'

type ErrorMessageProperties = {
  /** Plain string message. */
  error?: FieldError
  message?: string
}

export const ErrorMessage = ({
  error,
  message
}: ErrorMessageProperties): JSX.Element | null => {
  const resolved =
    message ??
    (error
      ? typeof error.message === 'string'
        ? error.message
        : String(error.message)
      : undefined)

  if (!resolved) return null

  return <p className={errorMessageStyle}>{resolved}</p>
}

// Default export removed — use named export `ErrorMessage`
