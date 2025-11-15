import type { SessionDetail } from '@/lib/api/session/getSession'
import { emitToast } from '@/lib/toastEvents'

import { useReferenceActions } from './useReferenceActions'

type UseSessionReferencesListHandlersProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  setSessionDetail: (data: SessionDetail | null) => void
  refreshSessions: () => Promise<void>
}

export const useSessionReferencesListHandlers = ({
  sessionDetail,
  currentSessionId,
  setSessionDetail,
  refreshSessions
}: UseSessionReferencesListHandlersProperties): {
  handleReferenceCheckboxChange: (index: number) => void
  handleReferencePersistToggle: (index: number) => void
  handleReferenceTtlChange: (index: number, action: 'increment' | 'decrement') => void
} => {
  const {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleUpdateReferenceDisabled
  } = useReferenceActions(sessionDetail, setSessionDetail, refreshSessions)

  const handleReferenceCheckboxChange = (index: number): void => {
    if (!currentSessionId || !sessionDetail) return
    const newReferences = [...sessionDetail.references]
    newReferences[index].disabled = !newReferences[index].disabled
    try {
      void handleUpdateReferenceDisabled(
        currentSessionId,
        index,
        newReferences[index].disabled
      )
      emitToast.success('Reference disabled state updated successfully')
    } catch (error: unknown) {
      emitToast.failure(
        (error as Error).message || 'Failed to update reference disabled state.'
      )
    }
  }

  const handleReferencePersistToggle = (index: number): void => {
    if (!currentSessionId || !sessionDetail) return
    const newReferences = [...sessionDetail.references]
    newReferences[index].persist = !newReferences[index].persist
    try {
      void handleUpdateReferencePersist(
        currentSessionId,
        index,
        newReferences[index].persist
      )
      emitToast.success('Reference persist state updated successfully')
    } catch (error: unknown) {
      emitToast.failure(
        (error as Error).message || 'Failed to update reference persist state.'
      )
    }
  }

  const handleReferenceTtlChange = (
    index: number,
    action: 'increment' | 'decrement'
  ): void => {
    if (!currentSessionId || !sessionDetail) return
    const newReferences = [...sessionDetail.references]
    const currentTtl = newReferences[index].ttl !== null ? newReferences[index].ttl : 3
    const newTtl =
      action === 'increment'
        ? (currentTtl || 0) + 1
        : Math.max(0, (currentTtl || 0) - 1)
    newReferences[index].ttl = newTtl
    try {
      void handleUpdateReferenceTtl(currentSessionId, index, newTtl)
      emitToast.success('Reference TTL updated successfully')
    } catch (error: unknown) {
      emitToast.failure((error as Error).message || 'Failed to update reference TTL.')
    }
  }

  return {
    handleReferenceCheckboxChange,
    handleReferencePersistToggle,
    handleReferenceTtlChange
  }
}
