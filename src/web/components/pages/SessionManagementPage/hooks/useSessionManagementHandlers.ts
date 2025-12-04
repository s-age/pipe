import { useState, useCallback } from 'react'

import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'

type UseSessionManagementActions = {
  archiveSessions: (sessionIds: string[]) => Promise<void>
  deleteArchivedSessions: (sessionIds: string[]) => Promise<void>
}

type Properties = {
  actions: UseSessionManagementActions
  navigate: (path: string) => void
}

export const useSessionManagementHandlers = ({
  actions,
  navigate
}: Properties): {
  currentTab: 'sessions' | 'archives'
  setCurrentTab: (tab: 'sessions' | 'archives') => void
  selectedSessionIds: string[]
  handleSelectSession: (sessionId: string, isSelected: boolean) => void
  handleSelectAll: (
    sessions: SessionOverview[] | SessionTreeNode[],
    isSelected: boolean
  ) => void
  handleBulkArchive: () => Promise<void>
  handleBulkDeleteArchived: () => Promise<void>
  handleCancel: () => void
} => {
  const [currentTab, setCurrentTab] = useState<'sessions' | 'archives'>('sessions')
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

  const handleBulkArchive = useCallback(async (): Promise<void> => {
    if (selectedSessionIds.length === 0) return
    try {
      await actions.archiveSessions(selectedSessionIds)
      setSelectedSessionIds([])
    } catch {
      // Error handled in actions
    }
  }, [actions, selectedSessionIds])

  const handleBulkDeleteArchived = useCallback(async (): Promise<void> => {
    if (selectedSessionIds.length === 0) return
    try {
      await actions.deleteArchivedSessions(selectedSessionIds)
      setSelectedSessionIds([])
    } catch {
      // Error handled in actions
    }
  }, [actions, selectedSessionIds])

  const handleSetCurrentTab = useCallback((tab: 'sessions' | 'archives') => {
    setCurrentTab(tab)
    setSelectedSessionIds([])
  }, [])

  const handleCancel = useCallback((): void => {
    navigate('/')
  }, [navigate])

  return {
    currentTab,
    setCurrentTab: handleSetCurrentTab,
    selectedSessionIds,
    handleSelectSession,
    handleSelectAll,
    handleBulkArchive,
    handleBulkDeleteArchived,
    handleCancel
  }
}
