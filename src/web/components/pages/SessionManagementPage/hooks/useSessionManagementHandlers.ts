import { useState, useCallback } from 'react'

import { getArchivedSessions } from '@/lib/api/session_management/getArchivedSessions'
import { getSessionTree } from '@/lib/api/sessionTree/getSessionTree'
import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'
import type { State } from '@/stores/useChatHistoryStore'
import { useSessionStore } from '@/stores/useChatHistoryStore'

import { useSessionManagementActions } from './useSessionManagementActions'
import { useSessionManagementLifecycle } from './useSessionManagementLifecycle'

type UseSessionManagementHandlersReturn = {
  currentTab: 'sessions' | 'archives'
  selectedSessionIds: string[]
  state: State
  handleBulkAction: () => Promise<void>
  handleCancel: () => void
  handleSelectAll: (
    sessions: SessionOverview[] | SessionTreeNode[],
    isSelected: boolean
  ) => void
  handleSelectSession: (sessionId: string, isSelected: boolean) => void
  setCurrentTab: (tab: 'sessions' | 'archives') => void
}

type Properties = {
  navigate: (path: string) => void
}

export const useSessionManagementHandlers = ({
  navigate
}: Properties): UseSessionManagementHandlersReturn => {
  // 1. Store initialization
  const { actions: storeActions, state } = useSessionStore()

  // 2. Actions hook
  const actions = useSessionManagementActions()

  // 3. Lifecycle hook
  useSessionManagementLifecycle({ storeActions })

  // 4. Local state and handlers
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
          // For archives, use filePath as unique identifier
          if ('filePath' in session && session.filePath) {
            ids.push(session.filePath)
          } else {
            ids.push(session.sessionId)
          }
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
    const success = await actions.archiveSessionsAction(selectedSessionIds)
    if (success) {
      // Refresh sessions after archiving
      const sessionTree = await getSessionTree()
      const sessions =
        sessionTree.sessionTree ||
        sessionTree.sessions.map(([_, overview]) => ({ ...overview, sessionId: _ }))
      storeActions.setSessions(sessions)
      // Refresh archived sessions
      const archivedSessions = await getArchivedSessions()
      storeActions.setArchivedSessions(archivedSessions)
      setSelectedSessionIds([])
    }
  }, [actions, selectedSessionIds, storeActions])

  const handleBulkDeleteArchived = useCallback(async (): Promise<void> => {
    if (selectedSessionIds.length === 0) return
    const success = await actions.deleteArchivedSessionsAction({
      filePaths: selectedSessionIds
    })
    if (success) {
      // Refresh archived sessions after deletion
      const archivedSessions = await getArchivedSessions()
      storeActions.setArchivedSessions(archivedSessions)
      setSelectedSessionIds([])
    }
  }, [actions, selectedSessionIds, storeActions])

  const handleSetCurrentTab = useCallback((tab: 'sessions' | 'archives') => {
    setCurrentTab(tab)
    setSelectedSessionIds([])
  }, [])

  const handleBulkAction = useCallback(async (): Promise<void> => {
    if (currentTab === 'sessions') {
      await handleBulkArchive()
    } else {
      await handleBulkDeleteArchived()
    }
  }, [currentTab, handleBulkArchive, handleBulkDeleteArchived])

  const handleCancel = useCallback((): void => {
    navigate('/')
  }, [navigate])

  // 5. Return unified interface
  return {
    state,
    currentTab,
    setCurrentTab: handleSetCurrentTab,
    selectedSessionIds,
    handleSelectSession,
    handleSelectAll,
    handleBulkAction,
    handleCancel
  }
}
