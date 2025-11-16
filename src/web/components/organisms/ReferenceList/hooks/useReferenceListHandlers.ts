import { useCallback } from 'react'
import type { UseFormReturn } from 'react-hook-form'

import type { Reference } from '@/types/reference'

export const useReferenceListHandlers = (
  formContext: UseFormReturn | undefined,
  _references: Reference[]
): {
  handleReferencesChange: (values: string[]) => void
} => {
  const handleReferencesChange = useCallback(
    (values: string[]): void => {
      if (formContext?.setValue) {
        // Convert values to Reference objects, keeping existing references
        const newReferences = values.map((value) => {
          const existing = _references.find((reference) => reference.path === value)

          return (
            existing || {
              path: value,
              disabled: false,
              ttl: 3,
              persist: false
            }
          )
        })
        formContext.setValue('references', newReferences)
      }
    },
    [formContext, _references]
  )

  return {
    handleReferencesChange
  }
}
