import { useCallback, useEffect, useMemo, useState } from 'react'
import type { UseFormReturn } from 'react-hook-form'

import type { SessionDetail } from '@/lib/api/session/getSession'
import { addToast } from '@/stores/useToastStore'
import type { Reference } from '@/types/reference'

import { useReferenceListActions } from './useReferenceListActions'

const STORAGE_KEY = 'referenceListAccordionOpen'

export const useReferenceListHandlers = (
  sessionDetail: SessionDetail,
  formContext: UseFormReturn | undefined
): {
  references: Reference[]
  existsValue: string[]
  accordionOpen: boolean
  setAccordionOpen: (open: boolean) => void
  handleReferencesChange: (values: string[]) => void
} => {
  const [references, setReferences] = useState<Reference[]>(
    sessionDetail.references || []
  )
  const [accordionOpen, setAccordionOpen] = useState(() => {
    // Load from localStorage on initial mount
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEY)

      return stored === 'true'
    }

    return false
  })

  // Persist accordion state to localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, String(accordionOpen))
  }, [accordionOpen])
  const { handleUpdateReference } = useReferenceListActions(
    sessionDetail.sessionId || null
  )

  const existsValue = useMemo(
    () => references.map((reference) => reference.path),
    [references]
  )

  const handleReferencesChange = useCallback(
    async (values: string[]): Promise<void> => {
      if (!formContext?.setValue) return

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

      // If there's no session yet, write references locally into the form
      // and component state so they are included in the final submit payload.
      if (!sessionDetail.sessionId) {
        formContext.setValue('references', newReferences)
        // wrote references locally
        setReferences(newReferences)

        return
      }

      try {
        const updatedReferences = await handleUpdateReference(newReferences)
        formContext.setValue('references', updatedReferences)
        // wrote references returned from server into the form context
        setReferences(updatedReferences || [])
      } catch {
        addToast({ status: 'failure', title: 'Failed to retrieve updated references.' })
      }
    },
    [formContext, references, handleUpdateReference, sessionDetail]
  )

  return {
    references,
    existsValue,
    accordionOpen,
    setAccordionOpen,
    handleReferencesChange
  }
}
