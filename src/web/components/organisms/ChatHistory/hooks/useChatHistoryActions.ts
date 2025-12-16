import { useCallback } from 'react'

import { deleteSession } from '@/lib/api/session/deleteSession'
import { getSession } from '@/lib/api/session/getSession'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { getSessionTree } from '@/lib/api/sessionTree/getSessionTree'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'
import { addToast } from '@/stores/useToastStore'
import { normalizeSessionTree } from '@/utils/normalizeSessionTree'

type UseChatHistoryActionsProperties = {
  currentSessionId: string | null
  refreshSessionsInStore: (
    sessionDetail: SessionDetail,
    sessions: SessionOverview[]
  ) => void
}

type UseChatHistoryActionsReturn = {
  deleteSessionAction: (sessionId: string) => Promise<void>
  refreshSession: () => Promise<void>
}

export const useChatHistoryActions = ({
  currentSessionId,
  refreshSessionsInStore
}: UseChatHistoryActionsProperties): UseChatHistoryActionsReturn => {
  // Session actions
  const deleteSessionAction = useCallback(async (sessionId: string): Promise<void> => {
    try {
      await deleteSession(sessionId)
      addToast({ status: 'success', title: 'Session deleted successfully' })
    } catch (error: unknown) {
      addToast({
        status: 'failure',
        title: (error as Error).message || 'Failed to delete session.'
      })
    }
  }, [])

  const refreshSession = useCallback(async (): Promise<void> => {
    if (!currentSessionId) return

    try {
      const fetchedSessionDetailResponse = await getSession(currentSessionId)
      const fetchedSessionTree = await getSessionTree()
      const newSessions = normalizeSessionTree(fetchedSessionTree)
      refreshSessionsInStore(fetchedSessionDetailResponse, newSessions)
    } catch (error: unknown) {
      addToast({
        status: 'failure',
        title: (error as Error).message || 'Failed to refresh session.'
      })
    }
  }, [currentSessionId, refreshSessionsInStore])

  return {
    // Session actions
    deleteSessionAction,
    refreshSession
  }
}
