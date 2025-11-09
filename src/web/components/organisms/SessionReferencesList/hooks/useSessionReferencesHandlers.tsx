import { useCallback } from 'react'
import type { ChangeEvent, MouseEvent } from 'react'

type SessionReferencesHandlersProperties = {
  handleReferenceCheckboxChange: (index: number) => void
  handleReferencePersistToggle: (index: number) => void
  handleReferenceTtlChange: (index: number, action: 'increment' | 'decrement') => void
}

export const useSessionReferencesHandlers = ({
  handleReferenceCheckboxChange,
  handleReferencePersistToggle,
  handleReferenceTtlChange
}: SessionReferencesHandlersProperties): {
  handleCheckboxChange: (event: ChangeEvent<HTMLInputElement>) => void
  handlePersistToggle: (event: MouseEvent<HTMLButtonElement>) => void
  handleTtlAction: (event: MouseEvent<HTMLButtonElement>) => void
} => {
  const handleCheckboxChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>): void => {
      const index = event.currentTarget.dataset.index
      if (!index) return
      handleReferenceCheckboxChange(Number(index))
    },
    [handleReferenceCheckboxChange]
  )

  const handlePersistToggle = useCallback(
    (event: MouseEvent<HTMLButtonElement>): void => {
      const index = event.currentTarget.dataset.index
      if (!index) return
      handleReferencePersistToggle(Number(index))
    },
    [handleReferencePersistToggle]
  )

  const handleTtlAction = useCallback(
    (event: MouseEvent<HTMLButtonElement>): void => {
      const index = event.currentTarget.dataset.index
      const action = event.currentTarget.dataset.action as
        | 'increment'
        | 'decrement'
        | undefined
      if (!index || !action) return
      handleReferenceTtlChange(Number(index), action)
    },
    [handleReferenceTtlChange]
  )

  return { handleCheckboxChange, handlePersistToggle, handleTtlAction }
}

// Default export removed — use named export `useSessionReferencesHandlers`
