import { useCallback, useMemo, useRef } from 'react'

import { useOptionalFormContext } from '@/components/organisms/Form'
import type { Reference } from '@/types/reference'

import { useReferenceActions } from './useReferenceActions'

export const useReferenceHandlers = (
  currentSessionId: string | null,
  reference: Reference,
  referenceIndex: number,
  setLocalReference?: React.Dispatch<React.SetStateAction<Reference>>
): {
  handlePersistToggle: (event: React.MouseEvent<HTMLButtonElement>) => Promise<void>
  handleTtlAction: (event: React.MouseEvent<HTMLButtonElement>) => Promise<void>
  handleChange: () => void
  handleToggleDisabled: () => Promise<void>
} => {
  const formContext = useOptionalFormContext()
  const {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleToggleReferenceDisabled
  } = useReferenceActions()

  const timeoutReference = useRef<NodeJS.Timeout | null>(null)

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

  const debouncedOnToggle = useMemo(
    (): (() => void) => () => {
      if (timeoutReference.current) {
        clearTimeout(timeoutReference.current)
      }
      timeoutReference.current = setTimeout(() => handleToggleDisabled(), 100)
    },
    [handleToggleDisabled]
  )

  const handleChange = useCallback(() => {
    debouncedOnToggle()
  }, [debouncedOnToggle])

  return {
    handlePersistToggle,
    handleTtlAction,
    handleChange,
    handleToggleDisabled
  }
}
