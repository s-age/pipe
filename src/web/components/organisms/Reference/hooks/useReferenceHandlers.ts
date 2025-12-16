import { useCallback, useEffect, useState } from 'react'

import { useOptionalFormContext } from '@/components/organisms/Form'
import type { Reference } from '@/types/reference'

import { useReferenceActions } from './useReferenceActions'

export const useReferenceHandlers = (
  currentSessionId: string | null,
  reference: Reference,
  referenceIndex: number,
  refreshSessions: () => Promise<void>
): {
  localReference: Reference
  setLocalReference: React.Dispatch<React.SetStateAction<Reference>>
  handlePersistToggle: (event: React.MouseEvent<HTMLButtonElement>) => Promise<void>
  handleTtlAction: (event: React.MouseEvent<HTMLButtonElement>) => Promise<void>
  handleToggleDisabled: () => Promise<void>
  handleToggle: () => void
} => {
  const [localReference, setLocalReference] = useState(reference)

  // Update local state when prop changes
  useEffect(() => {
    setLocalReference(reference)
  }, [reference])
  const formContext = useOptionalFormContext()
  const {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleToggleReferenceDisabled
  } = useReferenceActions(refreshSessions)

  const updateReferences = useCallback(
    (updater: (reference_: Reference) => Reference) => {
      const currentReferences = formContext?.getValues?.('references') || []
      const updatedReferences = [...currentReferences]
      updatedReferences[referenceIndex] = updater(updatedReferences[referenceIndex])
      formContext?.setValue?.('references', updatedReferences, {
        shouldDirty: true
      })
    },
    [formContext, referenceIndex]
  )

  const handlePersistToggle = useCallback(
    async (_event: React.MouseEvent<HTMLButtonElement>) => {
      if (!currentSessionId) return

      // Intentionally not awaiting - errors are handled in Actions layer
      void handleUpdateReferencePersist(
        currentSessionId,
        referenceIndex,
        !reference.persist
      )
      // Update local state for immediate UI feedback
      setLocalReference?.((previous) => ({ ...previous, persist: !previous.persist }))
    },
    [
      reference,
      referenceIndex,
      currentSessionId,
      handleUpdateReferencePersist,
      setLocalReference
    ]
  )

  const handleToggleDisabled = useCallback(async () => {
    if (!currentSessionId) return

    // Intentionally not awaiting - errors are handled in Actions layer
    void handleToggleReferenceDisabled(currentSessionId, referenceIndex)

    updateReferences((reference) => ({ ...reference, disabled: !reference.disabled }))

    // Update local state for immediate UI feedback
    setLocalReference?.((previous) => ({ ...previous, disabled: !previous.disabled }))
  }, [
    referenceIndex,
    currentSessionId,
    handleToggleReferenceDisabled,
    updateReferences,
    setLocalReference
  ])

  const handleTtlAction = useCallback(
    async (event: React.MouseEvent<HTMLButtonElement>) => {
      if (!currentSessionId) return
      const action = event.currentTarget.dataset.action
      const currentTtl = reference.ttl ?? 3
      let newTtl = currentTtl
      if (action === 'increment') {
        newTtl = currentTtl + 1
      } else if (action === 'decrement' && currentTtl > 0) {
        newTtl = currentTtl - 1
      }

      // Intentionally not awaiting - errors are handled in Actions layer
      void handleUpdateReferenceTtl(currentSessionId, referenceIndex, newTtl)

      updateReferences((reference) => ({ ...reference, ttl: newTtl }))

      // Update local state for immediate UI feedback
      setLocalReference?.((previous) => ({ ...previous, ttl: newTtl }))
    },
    [
      reference,
      referenceIndex,
      currentSessionId,
      handleUpdateReferenceTtl,
      updateReferences,
      setLocalReference
    ]
  )

  const handleToggle = useCallback(() => {
    // Intentionally not awaiting - errors are handled in Actions layer
    void handleToggleDisabled()
  }, [handleToggleDisabled])

  return {
    localReference,
    setLocalReference,
    handlePersistToggle,
    handleTtlAction,
    handleToggleDisabled,
    handleToggle
  }
}
