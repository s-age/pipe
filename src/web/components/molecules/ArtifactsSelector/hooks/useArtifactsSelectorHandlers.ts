import { useCallback } from 'react'
import type { UseFormReturn } from 'react-hook-form'

export const useArtifactsSelectorHandlers = (
  formContext: UseFormReturn | undefined
): {
  handleArtifactsChange: (values: string[]) => void
} => {
  const setValue = formContext?.setValue

  const handleArtifactsChange = useCallback(
    (values: string[]) => {
      if (setValue) {
        setValue('artifacts', values)
      }
    },
    [setValue]
  )

  return {
    handleArtifactsChange
  }
}
