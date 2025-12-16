import { useState, useCallback } from 'react'

import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'
import type { State } from '@/stores/useChatHistoryStore'
import { useSessionStore } from '@/stores/useChatHistoryStore'

import { useSessionManagementActions } from './useSessionManagementActions'
import { useSessionManagementLifecycle } from './useSessionManagementLifecycle'

type UseSessionManagementHandlersReturn = {
  state: State
  currentTab: 'sessions' | 'archives'
  setCurrentTab: (tab: 'sessions' | 'archives') => void
  selectedSessionIds: string[]
  handleSelectSession: (sessionId: string, isSelected: boolean) => void
  handleSelectAll: (
    sessions: SessionOverview[] | SessionTreeNode[],
    isSelected: boolean
  ) => void
  handleBulkAction: () => Promise<void>
  handleCancel: () => void
}

type Properties = {
  navigate: (path: string) => void
}

export const useSessionManagementHandlers = ({
  navigate
}: Properties): UseSessionManagementHandlersReturn => {
  // 1. Store initialization
  const { state, actions: storeActions } = useSessionStore()

  // 2. Actions hook
  const actions = useSessionManagementActions({ storeActions })

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
      // selectedSessionIds now contains filePaths for archives
      // Pass them directly to the delete action
      await actions.deleteArchivedSessions({
        filePaths: selectedSessionIds
      })
      setSelectedSessionIds([])
    } catch {
      // Error handled in actions
    }
  }, [actions, selectedSessionIds])

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
