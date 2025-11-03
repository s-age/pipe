import { JSX } from 'react'

import { errorMessageStyle } from './style.css'

type ErrorMessageProps = {
  message: string
}

const ErrorMessage = ({ message }: ErrorMessageProps): JSX.Element => (
  <p className={errorMessageStyle}>{message}</p>
)

export default ErrorMessage
