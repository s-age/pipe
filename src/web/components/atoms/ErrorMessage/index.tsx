import type { JSX } from 'react'
import type { FieldError } from 'react-hook-form'

import { errorMessageStyle } from './style.css'

type ErrorMessageProperties = {
  /** Plain string message. */
  message?: string
  /** react-hook-form FieldError */
  error?: FieldError
}

const ErrorMessage = ({
  message,
  error,
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

export default ErrorMessage
