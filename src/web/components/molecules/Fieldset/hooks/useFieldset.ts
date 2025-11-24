import { useId } from 'react'

type FieldsetIds = {
  hintId?: string
  errorId?: string
}

export const useFieldset = (hint?: unknown, error?: unknown): FieldsetIds => {
  const baseId = useId()
  const hintId = hint ? `${baseId}-hint` : undefined
  const errorId = error ? `${baseId}-error` : undefined

  return { hintId, errorId }
}
