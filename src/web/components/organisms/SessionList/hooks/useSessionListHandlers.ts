import { useCallback } from 'react'

import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'

export const useSessionListHandlers = (
  sessions: SessionOverview[] | SessionTreeNode[],
  allSelected: boolean,
  onSelectAll: (
    sessions: SessionOverview[] | SessionTreeNode[],
    isSelected: boolean
  ) => void
): { handleSelectAll: () => void } => {
  const handleSelectAll = useCallback((): void => {
    onSelectAll(sessions, !allSelected)
  }, [sessions, allSelected, onSelectAll])

  return {
    handleSelectAll
  }
}
