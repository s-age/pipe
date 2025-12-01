import { useState, useCallback } from 'react'

import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'

type UseSessionManagementActions = {
  deleteSessions: (sessionIds: string[]) => Promise<void>
}

type Properties = {
  actions: UseSessionManagementActions
}

export const useSessionManagementHandlers = ({
  actions
}: Properties): {
  selectedSessionIds: string[]
  handleSelectSession: (sessionId: string, isSelected: boolean) => void
  handleSelectAll: (
    sessions: SessionOverview[] | SessionTreeNode[],
    isSelected: boolean
  ) => void
  handleBulkDelete: () => Promise<void>
} => {
  const [selectedSessionIds, setSelectedSessionIds] = useState<string[]>([])

  const handleSelectSession = useCallback<
    (sessionId: string, isSelected: boolean) => void
  >((sessionId: string, isSelected: boolean): void => {
    setSelectedSessionIds((previous) =>
      isSelected ? [...previous, sessionId] : previous.filter((id) => id !== sessionId)
    )
  }, [])

  const handleSelectAll = useCallback<
    (sessions: SessionOverview[] | SessionTreeNode[], isSelected: boolean) => void
  >((sessions: SessionOverview[] | SessionTreeNode[], isSelected: boolean): void => {
    const getAllSessionIds = (
      items: SessionOverview[] | SessionTreeNode[]
    ): string[] => {
      const ids: string[] = []
      const collectIds = (sessions: SessionOverview[] | SessionTreeNode[]): void => {
        sessions.forEach((session) => {
          ids.push(session.session_id)
          if ('children' in session && session.children) {
            collectIds(session.children)
          }
        })
      }
      collectIds(items)

      return ids
    }
    const sessionIds = getAllSessionIds(sessions)
    setSelectedSessionIds(isSelected ? sessionIds : [])
  }, [])

  const handleBulkDelete = useCallback(async (): Promise<void> => {
    if (selectedSessionIds.length === 0) return
    try {
      await actions.deleteSessions(selectedSessionIds)
      setSelectedSessionIds([])
    } catch {
      // Error handled in actions
    }
  }, [actions, selectedSessionIds])

  return {
    selectedSessionIds,
    handleSelectSession,
    handleSelectAll,
    handleBulkDelete
  }
}
