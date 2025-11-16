import { useCallback, useState } from 'react'
import type { UseFormReturn } from 'react-hook-form'

import type { SessionDetail } from '@/lib/api/session/getSession'
import { emitToast } from '@/lib/toastEvents'
import type { Reference } from '@/types/reference'

import { useReferenceListActions } from './useReferenceListActions'

export const useReferenceListHandlers = (
  sessionDetail: SessionDetail,
  formContext: UseFormReturn | undefined
): {
  references: Reference[]
  handleReferencesChange: (values: string[]) => void
} => {
  const [references, setReferences] = useState(sessionDetail.references || [])
  const { handleUpdateReference } = useReferenceListActions(
    sessionDetail.session_id || null
  )

  const handleReferencesChange = useCallback(
    async (values: string[]): Promise<void> => {
      if (formContext?.setValue) {
        // Convert values to Reference objects, keeping existing references
        const newReferences = values.map(
          (value) =>
            references.find((reference) => reference.path === value) || {
              path: value,
              disabled: false,
              ttl: 3,
              persist: false
            }
        )

        try {
          const updatedReferences = await handleUpdateReference(newReferences)
          formContext.setValue('references', updatedReferences)
          setReferences(updatedReferences || [])
          console.log({ updatedReferences })
        } catch {
          emitToast.failure('Failed to retrieve updated references.')
        }
      }
    },
    [formContext, references, handleUpdateReference]
  )

  return {
    references,
    handleReferencesChange
  }
}
