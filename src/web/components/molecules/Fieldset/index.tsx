import type { JSX, ReactNode } from 'react'
import type { FieldError } from 'react-hook-form'

import { ErrorMessage } from '@/components/atoms/ErrorMessage'
import { Legend } from '@/components/atoms/Legend'

import { useFieldset } from './hooks/useFieldset'
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

export const Fieldset = ({
  legend,
  hint,
  error,
  children,
  className
}: FieldsetProperties): JSX.Element => {
  const ids = useFieldset(hint, error)
  const { hintId, errorId } = ids

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

// Default export removed — use named export `Fieldset`
