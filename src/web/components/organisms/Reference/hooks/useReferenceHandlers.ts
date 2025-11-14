import { useCallback } from 'react'
import type { UseFormReturn } from 'react-hook-form'

import type { Reference } from '@/types/reference'

import { useReferenceActions } from './useReferenceActions'

export const useReferenceHandlers = (
  currentSessionId: string | null,
  reference: Reference,
  referenceIndex: number,
  formContext?: UseFormReturn,
  setLocalReference?: React.Dispatch<React.SetStateAction<Reference>>
): {
  handlePersistToggle: (event: React.MouseEvent<HTMLButtonElement>) => Promise<void>
  handleToggleDisabled: () => Promise<void>
  handleTtlAction: (event: React.MouseEvent<HTMLButtonElement>) => Promise<void>
} => {
  const {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleToggleReferenceDisabled
  } = useReferenceActions()

  const handlePersistToggle = useCallback(
    async (_event: React.MouseEvent<HTMLButtonElement>) => {
      if (!currentSessionId) return

      const newPersist = !reference.persist
      try {
        await handleUpdateReferencePersist(currentSessionId, referenceIndex, newPersist)

        // Update local state for immediate UI feedback
        setLocalReference?.((previous) => ({ ...previous, persist: newPersist }))
      } catch (error) {
        console.error('Failed to update persist:', error)
      }
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

    try {
      await handleToggleReferenceDisabled(currentSessionId, referenceIndex)

      // Update the form state by getting current references and updating the specific one
      const currentReferences = formContext?.getValues?.('references') || []
      const updatedReferences = [...currentReferences]
      updatedReferences[referenceIndex] = {
        ...updatedReferences[referenceIndex],
        disabled: !updatedReferences[referenceIndex].disabled
      }
      formContext?.setValue?.('references', updatedReferences, {
        shouldDirty: true
      })

      // Update local state for immediate UI feedback
      setLocalReference?.((previous) => ({ ...previous, disabled: !previous.disabled }))
    } catch (error) {
      console.error('Failed to toggle reference:', error)
    }
  }, [
    referenceIndex,
    currentSessionId,
    formContext,
    handleToggleReferenceDisabled,
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
      } else {
        return
      }

      try {
        await handleUpdateReferenceTtl(currentSessionId, referenceIndex, newTtl)
        // Update the form state by getting current references and updating the specific one
        const currentReferences = formContext?.getValues?.('references') || []
        const updatedReferences = [...currentReferences]
        updatedReferences[referenceIndex] = {
          ...updatedReferences[referenceIndex],
          ttl: newTtl
        }
        formContext?.setValue?.('references', updatedReferences, {
          shouldDirty: true
        })

        // Update local state for immediate UI feedback
        setLocalReference?.((previous) => ({ ...previous, ttl: newTtl }))
      } catch (error) {
        console.error('Failed to update TTL:', error)
      }
    },
    [
      reference,
      referenceIndex,
      formContext,
      currentSessionId,
      handleUpdateReferenceTtl,
      setLocalReference
    ]
  )

  return {
    handlePersistToggle,
    handleToggleDisabled,
    handleTtlAction
  }
}
