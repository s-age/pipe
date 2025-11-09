import type { SessionDetail } from '@/lib/api/session/getSession'

import { useReferenceActions } from './useReferenceActions'

type UseSessionReferencesListLogicProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  setSessionDetail: (data: SessionDetail | null) => void
  refreshSessions: () => Promise<void>
}

export const useSessionReferencesListLogic = ({
  sessionDetail,
  currentSessionId,
  setSessionDetail,
  refreshSessions,
}: UseSessionReferencesListLogicProperties): {
  handleReferenceCheckboxChange: (index: number) => void
  handleReferencePersistToggle: (index: number) => void
  handleReferenceTtlChange: (index: number, action: 'increment' | 'decrement') => void
} => {
  const {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleUpdateReferenceDisabled,
  } = useReferenceActions(sessionDetail, setSessionDetail, refreshSessions)

  const handleReferenceCheckboxChange = (index: number): void => {
    if (!currentSessionId || !sessionDetail) return
    const newReferences = [...sessionDetail.references]
    newReferences[index].disabled = !newReferences[index].disabled
    handleUpdateReferenceDisabled(
      currentSessionId,
      index,
      newReferences[index].disabled,
    )
  }

  const handleReferencePersistToggle = (index: number): void => {
    if (!currentSessionId || !sessionDetail) return
    const newReferences = [...sessionDetail.references]
    newReferences[index].persist = !newReferences[index].persist
    handleUpdateReferencePersist(currentSessionId, index, newReferences[index].persist)
  }

  const handleReferenceTtlChange = (
    index: number,
    action: 'increment' | 'decrement',
  ): void => {
    if (!currentSessionId || !sessionDetail) return
    const newReferences = [...sessionDetail.references]
    const currentTtl = newReferences[index].ttl !== null ? newReferences[index].ttl : 3
    const newTtl =
      action === 'increment'
        ? (currentTtl || 0) + 1
        : Math.max(0, (currentTtl || 0) - 1)
    newReferences[index].ttl = newTtl
    handleUpdateReferenceTtl(currentSessionId, index, newTtl)
  }

  return {
    handleReferenceCheckboxChange,
    handleReferencePersistToggle,
    handleReferenceTtlChange,
  }
}
