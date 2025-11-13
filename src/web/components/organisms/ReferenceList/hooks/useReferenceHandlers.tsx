import { useCallback } from 'react'
import type { ChangeEvent, MouseEvent } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'

import { useReferenceActions } from './useReferenceActions'

type UseReferenceControlsProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  refreshSessions?: () => Promise<void>
}

export const useReferenceControls = ({
  sessionDetail,
  currentSessionId,
  refreshSessions
}: UseReferenceControlsProperties): {
  // DOM-ready handlers
  handleCheckboxChange: (event: ChangeEvent<HTMLInputElement>) => void
  handlePersistToggle: (event: MouseEvent<HTMLButtonElement>) => void
  handleTtlAction: (event: MouseEvent<HTMLButtonElement>) => void
  // programmatic functions (useful for tests or alternative UI flows)
  toggleDisabled: (index: number) => void
  togglePersist: (index: number) => void
  changeTtl: (index: number, action: 'increment' | 'decrement') => void
  handleAddReference: (path: string) => Promise<void>
} => {
  // We keep API actions separated for testability / reuse
  const {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleUpdateReferenceDisabled,
    handleAddReference: addReference
  } = useReferenceActions(sessionDetail, refreshSessions)

  const toggleDisabled = useCallback(
    (index: number): void => {
      if (!currentSessionId || !sessionDetail) return

      const newReferences = [...sessionDetail.references]
      newReferences[index] = {
        ...newReferences[index],
        disabled: !newReferences[index].disabled
      }

      handleUpdateReferenceDisabled(
        currentSessionId,
        index,
        !!newReferences[index].disabled
      )
    },
    [currentSessionId, sessionDetail, handleUpdateReferenceDisabled]
  )

  const togglePersist = useCallback(
    (index: number): void => {
      if (!currentSessionId || !sessionDetail) return

      const newReferences = [...sessionDetail.references]
      newReferences[index] = {
        ...newReferences[index],
        persist: !newReferences[index].persist
      }

      handleUpdateReferencePersist(
        currentSessionId,
        index,
        !!newReferences[index].persist
      )
    },
    [currentSessionId, sessionDetail, handleUpdateReferencePersist]
  )

  const changeTtl = useCallback(
    (index: number, action: 'increment' | 'decrement'): void => {
      if (!currentSessionId || !sessionDetail) return

      const newReferences = [...sessionDetail.references]
      const currentTtl =
        newReferences[index].ttl !== null ? newReferences[index].ttl : 3

      const newTtl =
        action === 'increment'
          ? (currentTtl || 0) + 1
          : Math.max(0, (currentTtl || 0) - 1)

      newReferences[index] = { ...newReferences[index], ttl: newTtl }

      handleUpdateReferenceTtl(currentSessionId, index, newTtl)
    },
    [currentSessionId, sessionDetail, handleUpdateReferenceTtl]
  )

  const handleCheckboxChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>): void => {
      const index = event.currentTarget.dataset.index
      if (!index) return
      toggleDisabled(Number(index))
    },
    [toggleDisabled]
  )

  const handlePersistToggle = useCallback(
    (event: MouseEvent<HTMLButtonElement>): void => {
      const index = event.currentTarget.dataset.index
      if (!index) return
      togglePersist(Number(index))
    },
    [togglePersist]
  )

  const handleTtlAction = useCallback(
    (event: MouseEvent<HTMLButtonElement>): void => {
      const index = event.currentTarget.dataset.index
      const action = event.currentTarget.dataset.action as
        | 'increment'
        | 'decrement'
        | undefined
      if (!index || !action) return
      changeTtl(Number(index), action)
    },
    [changeTtl]
  )

  const handleAddReference = useCallback(
    async (path: string): Promise<void> => {
      if (!currentSessionId) return
      await addReference(currentSessionId, path)
    },
    [currentSessionId, addReference]
  )

  return {
    handleCheckboxChange,
    handlePersistToggle,
    handleTtlAction,
    toggleDisabled,
    togglePersist,
    changeTtl,
    handleAddReference
  }
}
