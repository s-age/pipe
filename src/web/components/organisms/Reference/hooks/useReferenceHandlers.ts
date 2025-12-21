import { useCallback, useState } from 'react'

import { useOptionalFormContext } from '@/components/organisms/Form'
import type { Reference } from '@/types/reference'

import { useReferenceActions } from './useReferenceActions'
import { useReferenceLifecycle } from './useReferenceLifecycle'

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

  // Lifecycle: sync props to local state
  useReferenceLifecycle({ reference, setLocalReference })

  const formContext = useOptionalFormContext()
  const {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleToggleReferenceDisabled
  } = useReferenceActions()

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

      // Update local state for immediate UI feedback
      setLocalReference?.((previous) => ({ ...previous, persist: !previous.persist }))

      await handleUpdateReferencePersist(
        currentSessionId,
        referenceIndex,
        !reference.persist
      )
      await refreshSessions()
    },
    [
      reference,
      referenceIndex,
      currentSessionId,
      handleUpdateReferencePersist,
      setLocalReference,
      refreshSessions
    ]
  )

  const handleToggleDisabled = useCallback(async () => {
    if (!currentSessionId) return

    updateReferences((reference) => ({ ...reference, disabled: !reference.disabled }))

    // Update local state for immediate UI feedback
    setLocalReference?.((previous) => ({ ...previous, disabled: !previous.disabled }))

    await handleToggleReferenceDisabled(currentSessionId, referenceIndex)
    await refreshSessions()
  }, [
    referenceIndex,
    currentSessionId,
    handleToggleReferenceDisabled,
    updateReferences,
    setLocalReference,
    refreshSessions
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

      updateReferences((reference) => ({ ...reference, ttl: newTtl }))

      // Update local state for immediate UI feedback
      setLocalReference?.((previous) => ({ ...previous, ttl: newTtl }))

      await handleUpdateReferenceTtl(currentSessionId, referenceIndex, newTtl)
      await refreshSessions()
    },
    [
      reference,
      referenceIndex,
      currentSessionId,
      handleUpdateReferenceTtl,
      updateReferences,
      setLocalReference,
      refreshSessions
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
