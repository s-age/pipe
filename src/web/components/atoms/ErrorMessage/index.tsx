import type { JSX } from 'react'

import { errorMessageStyle } from './style.css'

type ErrorMessageProperties = {
  message: string
}

const ErrorMessage = ({ message }: ErrorMessageProperties): JSX.Element => (
  <p className={errorMessageStyle}>{message}</p>
)

export default ErrorMessage
