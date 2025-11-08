import { useId } from 'react'
import type { JSX, ReactNode } from 'react'
import type { FieldError } from 'react-hook-form'

import ErrorMessage from '@/components/atoms/ErrorMessage'
import Legend from '@/components/atoms/Legend'

import * as styles from './style.css'

type FieldsetIds = {
  hintId?: string
  errorId?: string
}

type FieldsetProperties = {
  legend: ReactNode
  hint?: ReactNode
  error?: ReactNode
  children: ReactNode | ((ids: FieldsetIds) => ReactNode)
  className?: string
}

const Fieldset = ({
  legend,
  hint,
  error,
  children,
  className,
}: FieldsetProperties): JSX.Element => {
  const baseId = useId()
  const hintId = hint ? `${baseId}-hint` : undefined
  const errorId = error ? `${baseId}-error` : undefined

  const ids: FieldsetIds = { hintId, errorId }

  return (
    <fieldset className={styles.fieldset + (className ? ` ${className}` : '')}>
      <Legend>{legend}</Legend>

      {typeof children === 'function' ? children(ids) : children}

      {hint ? (
        <p id={hintId} className={styles.hint} aria-hidden={!!error}>
          {hint}
        </p>
      ) : null}
      {error ? (
        <div id={errorId} role="alert">
          {typeof error === 'string' ? (
            <ErrorMessage message={error} />
          ) : error &&
            typeof error === 'object' &&
            'message' in (error as FieldError) ? (
            <ErrorMessage error={error as FieldError} />
          ) : (
            error
          )}
        </div>
      ) : null}
    </fieldset>
  )
}

export default Fieldset
