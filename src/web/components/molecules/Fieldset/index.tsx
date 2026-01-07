import type { JSX, ReactNode } from 'react'
import type { FieldError } from 'react-hook-form'

import { ErrorMessage } from '@/components/atoms/ErrorMessage'
import { Legend } from '@/components/atoms/Legend'
import { Box } from '@/components/molecules/Box'
import { Paragraph } from '@/components/molecules/Paragraph'

import { useFieldset } from './hooks/useFieldset'
import * as styles from './style.css'

type FieldsetIds = {
  errorId?: string
  hintId?: string
}

type FieldsetProperties = {
  children: ReactNode | ((ids: FieldsetIds) => ReactNode)
  legend: ReactNode
  className?: string
  error?: ReactNode
  hint?: ReactNode
}

export const Fieldset = ({
  children,
  legend,
  className,
  error,
  hint
}: FieldsetProperties): JSX.Element => {
  const ids = useFieldset(hint, error)
  const { errorId, hintId } = ids

  return (
    <fieldset className={styles.fieldset + (className ? ` ${className}` : '')}>
      <Legend>{legend}</Legend>

      {typeof children === 'function' ? children(ids) : children}

      {hint ? (
        <Paragraph id={hintId} className={styles.hint} aria-hidden={!!error}>
          {hint}
        </Paragraph>
      ) : null}
      {error ? (
        <Box id={errorId} role="alert">
          {typeof error === 'string' ? (
            <ErrorMessage message={error} />
          ) : error &&
            typeof error === 'object' &&
            'message' in (error as FieldError) ? (
            <ErrorMessage error={error as FieldError} />
          ) : (
            error
          )}
        </Box>
      ) : null}
    </fieldset>
  )
}

// Default export removed — use named export `Fieldset`
